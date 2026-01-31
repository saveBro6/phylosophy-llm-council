import { createContext, useContext, useMemo, useState } from 'react';
import { councilMembers } from '../config/councilLayout';

const CouncilContext = createContext(null);

// Map backend `philosophier` identifiers to on-screen member ids so we can
// index stage data by member id in the frontend.
const PHILOSOPHIER_TO_MEMBER_ID = councilMembers.reduce((acc, member) => {
  if (member.philosophierKey) {
    acc[member.philosophierKey] = member.id;
  }
  return acc;
}, {});

function deriveFromConversation(conversation) {
  if (!conversation || !Array.isArray(conversation.messages)) {
    return {
      latestAssistant: null,
      assistantTurnKey: null,
      stage1ByMemberId: {},
      stage2ByMemberId: {},
      stage3Final: null,
      metadata: null,
      loading: { stage1: false, stage2: false, stage3: false },
    };
  }

  let latestAssistant = null;
  let latestAssistantIndex = -1;

  for (let i = conversation.messages.length - 1; i >= 0; i -= 1) {
    const msg = conversation.messages[i];
    if (msg && msg.role === 'assistant') {
      latestAssistant = msg;
      latestAssistantIndex = i;
      break;
    }
  }

  const assistantTurnKey =
    latestAssistant && latestAssistantIndex >= 0
      ? `${conversation.id || 'conv'}-${latestAssistantIndex}`
      : null;

  const stage1ByMemberId = {};
  const stage2ByMemberId = {};
  let stage3Final = null;
  let metadata = null;

  if (latestAssistant?.stage1 && Array.isArray(latestAssistant.stage1)) {
    latestAssistant.stage1.forEach((item) => {
      if (!item || !item.philosophier) return;
      const memberId = PHILOSOPHIER_TO_MEMBER_ID[item.philosophier];
      if (!memberId) return;
      stage1ByMemberId[memberId] = item;
    });
  }

  if (latestAssistant?.stage2 && Array.isArray(latestAssistant.stage2)) {
    latestAssistant.stage2.forEach((item) => {
      if (!item || !item.philosophier) return;
      const memberId = PHILOSOPHIER_TO_MEMBER_ID[item.philosophier];
      if (!memberId) return;
      stage2ByMemberId[memberId] = item;
    });
  }

  if (latestAssistant?.stage3) {
    stage3Final = latestAssistant.stage3;
  }

  if (latestAssistant?.metadata) {
    metadata = latestAssistant.metadata;
  }

  const loading = {
    stage1: Boolean(latestAssistant?.loading?.stage1),
    stage2: Boolean(latestAssistant?.loading?.stage2),
    stage3: Boolean(latestAssistant?.loading?.stage3),
  };

  return {
    latestAssistant,
    assistantTurnKey,
    stage1ByMemberId,
    stage2ByMemberId,
    stage3Final,
    metadata,
    loading,
  };
}

export function CouncilProvider({ conversation, children }) {
  const [selectedMemberId, setSelectedMemberId] = useState(null);
  const [selectedStage, setSelectedStage] = useState(null);

  const derived = useMemo(
    () => deriveFromConversation(conversation),
    [conversation],
  );

  const value = useMemo(
    () => ({
      conversation,
      ...derived,
      selectedMemberId,
      setSelectedMemberId,
      selectedStage,
      setSelectedStage,
    }),
    [conversation, derived, selectedMemberId, selectedStage],
  );

  return (
    <CouncilContext.Provider value={value}>{children}</CouncilContext.Provider>
  );
}

export function useCouncil() {
  const ctx = useContext(CouncilContext);
  if (!ctx) {
    throw new Error('useCouncil must be used within a CouncilProvider');
  }
  return ctx;
}

