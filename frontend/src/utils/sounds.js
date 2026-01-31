let applauseAudio;

export function playApplause() {
  if (typeof window === 'undefined') return;

  try {
    if (!applauseAudio) {
      // The file should be placed in frontend/public/applause.mp3
      applauseAudio = new Audio('/applause.mp3');
      applauseAudio.volume = 0.7;
    } else {
      applauseAudio.currentTime = 0;
    }

    // Play may be blocked until user interaction; ignore errors.
    applauseAudio.play().catch(() => {});
  } catch (error) {
    console.warn('Failed to play applause sound:', error);
  }
}

