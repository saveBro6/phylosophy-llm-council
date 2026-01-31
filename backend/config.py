"""Configuration for the LLM Council."""


import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("backend.config")

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ElevenLabs TTS (optional)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# JSON array of 5 voice IDs: [Lenin, Plato, Descartes, Nietzsche, Khổng Tử]
_voice_ids_raw = os.getenv("ELEVENLABS_VOICE_IDS") or os.getenv("ELEVENLABS_VOICE_ID")
if _voice_ids_raw:
    try:
        ELEVENLABS_VOICE_IDS = json.loads(_voice_ids_raw)
        if not isinstance(ELEVENLABS_VOICE_IDS, list) or len(ELEVENLABS_VOICE_IDS) != 5:
            logger.warning("ELEVENLABS_VOICE_IDS is not a list of 5 items; ignoring value")
            ELEVENLABS_VOICE_IDS = None
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Failed to parse ELEVENLABS_VOICE_ID(S): %s", str(e))
        ELEVENLABS_VOICE_IDS = None
else:
    ELEVENLABS_VOICE_IDS = None

# Council members - list of OpenRouter model identifiers
COUNCIL_MODELS = [
    "arcee-ai/trinity-large-preview:free",
    "arcee-ai/trinity-large-preview:free",
    "arcee-ai/trinity-large-preview:free",
    "z-ai/glm-4.5-air:free",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "arcee-ai/trinity-large-preview:free"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
