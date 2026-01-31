import { useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { isTtsSupported, speak, stopSpeaking } from '../utils/tts';
import './SpeechBubble.css';

const STREAM_INTERVAL_MS = 20;
const STREAM_CHUNK_SIZE = 3;

export default function SpeechBubble({
  member,
  stage,
  fullText,
  isStreaming,
  onClose,
}) {
  const [displayedText, setDisplayedText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);

  const title = useMemo(() => {
    if (stage === 'stage1') {
      return `${member.displayName} – Individual Answer`;
    }
    if (stage === 'stage2') {
      return `${member.displayName} – Critique of Others`;
    }
    if (stage === 'stage3') {
      return `${member.displayName} – Final Verdict`;
    }
    return member.displayName;
  }, [member.displayName, stage]);

  useEffect(() => {
    if (!fullText) {
      setDisplayedText('');
      return undefined;
    }

    let index = 0;
    const text = fullText;
    setDisplayedText('');

    const id = window.setInterval(() => {
      index += STREAM_CHUNK_SIZE;
      setDisplayedText(text.slice(0, index));
      if (index >= text.length) {
        window.clearInterval(id);
      }
    }, STREAM_INTERVAL_MS);

    return () => window.clearInterval(id);
  }, [fullText]);

  useEffect(() => {
    // Stop TTS when bubble is unmounted or text changes significantly
    return () => {
      stopSpeaking();
      setIsSpeaking(false);
    };
  }, []);

  const handleToggleTts = () => {
    if (!isTtsSupported()) return;

    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
    } else if (fullText) {
      speak(fullText, {
        memberId: member.id,
        onEnd: () => setIsSpeaking(false),
        onError: () => setIsSpeaking(false),
      });
      setIsSpeaking(true);
    }
  };

  const hasContent = Boolean(fullText && fullText.trim().length > 0);

  const isChairman = member.role === 'chairman';

  return (
    <div
      className={`speech-bubble-root${isChairman ? ' speech-bubble-chairman' : ''}`}
    >
      <div className="speech-bubble-header">
        <div className="speech-bubble-title">{title}</div>
        <div className="speech-bubble-actions">
          {isTtsSupported() && hasContent && (
            <button
              type="button"
              className={`speech-bubble-icon-button ${
                isSpeaking ? 'active' : ''
              }`}
              onClick={handleToggleTts}
              aria-label={isSpeaking ? 'Stop voice' : 'Play voice'}
            >
              {isSpeaking ? '■' : '🔊'}
            </button>
          )}
          <button
            type="button"
            className="speech-bubble-icon-button"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>
      </div>

      <div className="speech-bubble-body">
        {!hasContent && isStreaming && (
          <div className="speech-bubble-placeholder">
            Đang suy nghĩ...
          </div>
        )}

        {!hasContent && !isStreaming && (
          <div className="speech-bubble-placeholder">
            Chưa có nội dung cho phần này.
          </div>
        )}

        {hasContent && (
          <div className="speech-bubble-text markdown-content">
            <ReactMarkdown>{displayedText}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

