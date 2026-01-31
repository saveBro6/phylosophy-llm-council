// Configuration for philosophers and chairman layout in the courtroom scene.
// Positions are expressed in percentages relative to the background image.

export const councilMembers = [
  {
    id: 'plato',
    displayName: 'Plato',
    role: 'philosopher',
    philosophierKey: 'Plato',
    // Mapped to first council model in backend/config.py
    modelId: 'arcee-ai/trinity-large-preview:free',
    position: { leftPct: 14, topPct: 56 },
  },
  {
    id: 'descartes',
    displayName: 'Descartes',
    role: 'philosopher',
    philosophierKey: 'Descartes',
    modelId: 'openai/gpt-oss-20b:free',
    position: { leftPct: 34, topPct: 54 },
  },
  {
    id: 'nietzsche',
    displayName: 'Nietzsche',
    role: 'philosopher',
    philosophierKey: 'Nietzsche',
    modelId: 'mistralai/mistral-small-3.1-24b-instruct:free',
    position: { leftPct: 66, topPct: 54 },
  },
  {
    id: 'confucius',
    displayName: 'Khổng Tử',
    role: 'philosopher',
    philosophierKey: 'Khổng Tử',
    modelId: 'z-ai/glm-4.5-air:free',
    position: { leftPct: 86, topPct: 56 },
  },
];

export const chairman = {
  id: 'lenin',
  displayName: 'Lenin',
  role: 'chairman',
  // Chairman model matches CHAIRMAN_MODEL in backend/config.py
  modelId: 'arcee-ai/trinity-large-preview:free',
  position: { leftPct: 50, topPct: 24 },
};

