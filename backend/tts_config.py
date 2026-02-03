"""TTS profiles per council member (from TTS_profile.md)."""

# member_id -> ElevenLabs voice_settings (0-1) and speed
# Order of ELEVENLABS_VOICE_ID list: lenin, plato, descartes, nietzsche, confucius
TTS_PROFILES = {
    "lenin": {
        "stability": 0.8,
        "similarity_boost": 0.9,
        "style": 0.6,
        "use_speaker_boost": True,
        "speed": 1.3,
    },
    "plato": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.2,
        "use_speaker_boost": True,
        "speed": 1.1,
    },
    "descartes": {
        "stability": 0.9,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True,
        "speed": 1.3,
    },
    "nietzsche": {
        "stability": 0.3,
        "similarity_boost": 0.75,
        "style": 0.8,
        "use_speaker_boost": True,
        "speed": 1.3,
    },
    "confucius": {
        "stability": 0.7,
        "similarity_boost": 0.75,
        "style": 0.1,
        "use_speaker_boost": True,
        "speed": 1.1,
    },
}

# Order of voice IDs in config: Lenin, Plato, Descartes, Nietzsche, Khổng Tử
MEMBER_IDS_ORDER = ["lenin", "plato", "descartes", "nietzsche", "confucius"]


def get_profile(member_id: str) -> dict:
    """Return voice_settings + speed for member_id; fallback to defaults."""
    return TTS_PROFILES.get(
        member_id,
        {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.0,
        },
    ).copy()
