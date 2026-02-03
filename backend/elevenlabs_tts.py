"""ElevenLabs TTS client using the official `elevenlabs` Python client.

This implementation calls the synchronous client inside a thread via
`asyncio.to_thread` so the FastAPI async handlers remain responsive.
"""

import logging
import asyncio
from typing import Optional
import types
from .config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_IDS
from .tts_config import get_profile, MEMBER_IDS_ORDER

# The `elevenlabs` package provides `ElevenLabs` client
try:
    from elevenlabs.client import ElevenLabs
except Exception:  # pragma: no cover - defensive if package missing
    ElevenLabs = None

logger = logging.getLogger("backend.elevenlabs_tts")

TTS_MODEL_ID = "eleven_v3"      #or eleven_turbo_v2_5
MAX_TEXT_LENGTH = 5000


def _get_voice_id(member_id: str) -> Optional[str]:
    if not ELEVENLABS_VOICE_IDS:
        return None
    try:
        idx = MEMBER_IDS_ORDER.index(member_id)
        return ELEVENLABS_VOICE_IDS[idx]
    except (ValueError, IndexError):
        return ELEVENLABS_VOICE_IDS[0] if ELEVENLABS_VOICE_IDS else None


async def synthesize(text: str, member_id: str) -> bytes | None:
    """Synthesize speech using the `ElevenLabs` client.

    Returns raw audio bytes (mp3) or None on failure.
    """
    if ElevenLabs is None:
        logger.error("elevenlabs package not installed")
        return None

    if not ELEVENLABS_API_KEY:
        logger.error("ElevenLabs API key not configured")
        return None

    voice_id = _get_voice_id(member_id)
    if not voice_id:
        logger.error("No voice_id available for member_id=%s", member_id)
        return None

    # Prepare client
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    except Exception as e:
        logger.exception("Failed to construct ElevenLabs client: %s", str(e))
        return None

    profile = get_profile(member_id)

    def _convert_sync() -> bytes | None:
        try:
            audio = client.text_to_speech.convert(
                text=text[:MAX_TEXT_LENGTH],
                voice_id=voice_id,
                model_id=TTS_MODEL_ID,
                output_format="mp3_44100_128",
            )
            # The client may return bytes, a file-like object, or an iterator/generator of chunks.
            if isinstance(audio, (bytes, bytearray)):
                return bytes(audio)

            if hasattr(audio, "read"):
                try:
                    return audio.read()
                except Exception:
                    try:
                        return bytes(audio)
                    except Exception:
                        logger.exception("Failed to read/convert file-like audio object")
                        return None

            # Handle generator/iterator that yields chunks
            if isinstance(audio, types.GeneratorType) or (hasattr(audio, "__iter__") and not isinstance(audio, (str, bytes, bytearray))):
                buf = bytearray()
                try:
                    for chunk in audio:
                        if chunk is None:
                            continue
                        if isinstance(chunk, (bytes, bytearray, memoryview)):
                            buf.extend(chunk)
                        elif isinstance(chunk, str):
                            buf.extend(chunk.encode("utf-8"))
                        else:
                            try:
                                buf.extend(bytes(chunk))
                            except Exception:
                                logger.warning("Skipping non-bytes chunk of type %s", type(chunk))
                    return bytes(buf)
                except Exception:
                    logger.exception("Failed while iterating audio chunks from ElevenLabs")
                    return None

            logger.error("Unexpected audio type returned from ElevenLabs: %s", type(audio))
            return None
        except Exception as e:
            logger.exception("ElevenLabs client.convert failed: %s", str(e))
            return None

    audio_bytes = await asyncio.to_thread(_convert_sync)
    if audio_bytes is None:
        logger.error("Synthesize returned no audio for member_id=%s", member_id)
    return audio_bytes
