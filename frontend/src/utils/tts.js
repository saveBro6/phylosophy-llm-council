import { api } from '../api';

let currentAudio = null;
let currentObjectUrl = null;

export function isTtsSupported() {
  return typeof window !== 'undefined';
}

/**
 * Speak text via ElevenLabs TTS (Vietnamese output).
 * @param {string} text - Text to synthesize
 * @param {object} options - { memberId: string, onEnd?: () => void, onError?: (err) => void }
 */
export async function speak(text, options = {}) {
  const cleanText = (text || '').trim();
  if (!cleanText) return;

  const memberId = options?.memberId;
  if (!memberId) {
    console.warn('TTS requires options.memberId (lenin, plato, descartes, nietzsche, confucius).');
    return;
  }

  stopSpeaking();

  try {
    const blob = await api.requestTts(cleanText, memberId);
    const objectUrl = URL.createObjectURL(blob);
    currentObjectUrl = objectUrl;
    const audio = new Audio(objectUrl);
    currentAudio = audio;
    const onEnd = options.onEnd;
    const onError = options.onError;

    audio.addEventListener('ended', () => {
      if (currentAudio === audio && currentObjectUrl) {
        URL.revokeObjectURL(currentObjectUrl);
        currentObjectUrl = null;
      }
      currentAudio = null;
      onEnd?.();
    });
    audio.addEventListener('error', () => {
      if (currentObjectUrl) {
        URL.revokeObjectURL(currentObjectUrl);
        currentObjectUrl = null;
      }
      currentAudio = null;
      onError?.(new Error('Audio playback failed'));
    });

    await audio.play();
  } catch (err) {
    console.error('TTS failed:', err);
    options.onError?.(err);
  }
}

export function stopSpeaking() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
  if (currentObjectUrl) {
    URL.revokeObjectURL(currentObjectUrl);
    currentObjectUrl = null;
  }
}
