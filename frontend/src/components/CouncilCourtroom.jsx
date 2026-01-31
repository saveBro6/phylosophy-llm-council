import { useState } from 'react';
import { councilMembers, chairman } from '../config/councilLayout';
import { useCouncil } from '../context/CouncilContext';
import { playApplause } from '../utils/sounds';
import SpeechBubble from './SpeechBubble';
import './CouncilCourtroom.css';

export default function CouncilCourtroom({ onSendMessage, isLoading }) {
  const {
    conversation,
    stage1ByMemberId,
    stage2ByMemberId,
    stage3Final,
    loading,
    selectedMemberId,
    setSelectedMemberId,
    selectedStage,
    setSelectedStage,
    assistantTurnKey,
  } = useCouncil();

  const [input, setInput] = useState('');

  const hasConversation = Boolean(conversation);

  const handleApplause = () => {
    playApplause();
  };

  const activeMember =
    councilMembers.find((m) => m.id === selectedMemberId) ||
    (selectedMemberId === chairman.id ? chairman : null);

  let activeText = '';
  let isBubbleStreaming = false;

  if (activeMember && selectedStage === 'stage1') {
    const data = stage1ByMemberId[activeMember.id];
    activeText = data?.response || '';
    isBubbleStreaming = loading.stage1;
  } else if (activeMember && selectedStage === 'stage2') {
    const data = stage2ByMemberId[activeMember.id];
    activeText = data?.critique || data?.ranking || '';
    isBubbleStreaming = loading.stage2;
  } else if (activeMember && selectedStage === 'stage3') {
    const data = stage3Final;
    activeText = data?.response || data?.text || '';
    isBubbleStreaming = loading.stage3;
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading && onSendMessage) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleMemberClick = (member) => {
    setSelectedMemberId(member.id);
    setSelectedStage('stage1');
  };

  const handleMemberContextMenu = (event, member) => {
    event.preventDefault();
    setSelectedMemberId(member.id);
    setSelectedStage('stage2');
  };

  const handleChairmanClick = () => {
    setSelectedMemberId(chairman.id);
    setSelectedStage('stage3');
  };

  const handleCloseBubble = () => {
    setSelectedMemberId(null);
    setSelectedStage(null);
  };

  return (
    <div className="courtroom-root">
      <div className="courtroom-scene">
        <div className="courtroom-overlay">
          {!hasConversation && (
            <div className="courtroom-empty-state">
              <h2>Welcome to the Philosophers&apos; Council</h2>
              <p>Create a new conversation on the left to begin.</p>
            </div>
          )}

          {hasConversation && conversation.messages.length === 0 && (
            <div className="courtroom-empty-state">
              <h2>Ask your first question</h2>
              <p>
                The council is waiting for your case. Type your question below
                to start the deliberation.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="courtroom-loading">
              <div className="courtroom-spinner" />
              <span>The council is deliberating...</span>
            </div>
          )}
        </div>

        <div className="courtroom-hotspots">
          {councilMembers.map((member) => (
            <button
              key={member.id}
              type="button"
              className={`courtroom-member ${
                selectedMemberId === member.id ? 'active' : ''
              }`}
              style={{
                left: `${member.position.leftPct}%`,
                top: `${member.position.topPct}%`,
              }}
              onClick={() => handleMemberClick(member)}
              onContextMenu={(event) =>
                handleMemberContextMenu(event, member)
              }
            >
              <span className="courtroom-member-label">
                {member.displayName}
              </span>
            </button>
          ))}

          <button
            type="button"
            className={`courtroom-chairman ${
              selectedMemberId === chairman.id ? 'active' : ''
            }`}
            style={{
              left: `${chairman.position.leftPct}%`,
              top: `${chairman.position.topPct}%`,
            }}
            onClick={handleChairmanClick}
          >
            <span className="courtroom-member-label">
              {chairman.displayName}
            </span>
          </button>

          {activeMember && selectedStage && (
            <div
              className="courtroom-bubble-wrapper"
              style={{
                left: `${activeMember.position.leftPct}%`,
                top: `${activeMember.position.topPct}%`,
              }}
            >
              <SpeechBubble
                member={activeMember}
                stage={selectedStage}
                fullText={activeText}
                isStreaming={isBubbleStreaming}
                onClose={handleCloseBubble}
              />
            </div>
          )}
        </div>
      </div>

      <form className="courtroom-input-bar" onSubmit={handleSubmit}>
        <textarea
          className="courtroom-input"
          placeholder="Ask your question to the council... (Shift+Enter for new line, Enter to send)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading || !hasConversation}
          rows={3}
        />
        <button
          type="submit"
          className="courtroom-send-button"
          disabled={!input.trim() || isLoading || !hasConversation}
        >
          Send
        </button>
      </form>

      <button
        type="button"
        className="courtroom-applause-button"
        onClick={handleApplause}
        aria-label="Play applause"
        title="Phát tiếng vỗ tay"
      >
        👏
      </button>
    </div>
  );
}

