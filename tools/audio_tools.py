import os
import pathlib
import wave
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from google.adk.tools import ToolContext

def wave_file(filename: str, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> str:
    """Saves raw PCM audio data into a standard WAV audio container."""
    path = pathlib.Path(filename).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    return str(path)

def generate_mock_pcm(duration_seconds: float = 1.0, rate: int = 24000) -> bytes:
    """Generates dummy 24 kHz 16-bit mono PCM bytes for offline testing."""
    total_samples = int(duration_seconds * rate)
    return bytes(total_samples * 2)  # 2 bytes per sample (16-bit)

def generate_podcast_audio(
    podcast_script: str,
    tool_context: Optional[ToolContext] = None,
    filename: str = "earnings_podcast",
    force_mock: bool = False
) -> Dict[str, Any]:
    """
    Generates multi-speaker podcast audio from script text using gemini-2.5-flash-preview-tts.

    Speakers:
      - Brenda (Bull analyst) -> Voice 'Kore'
      - Sam (Bear skeptic)   -> Voice 'Puck'

    Args:
        podcast_script: Dialogue formatted text ('Brenda: ... \n Sam: ...').
        tool_context: Optional ADK ToolContext.
        filename: Target WAV filename or path.
        force_mock: If True, bypasses API and generates test PCM audio.

    Returns:
        Dictionary with status, file path, and byte size.
    """
    if not filename.endswith(".wav"):
        filename += ".wav"
    file_path = pathlib.Path(filename).resolve()

    if force_mock:
        pcm_bytes = generate_mock_pcm(duration_seconds=2.0)
        saved_path = wave_file(str(file_path), pcm_bytes)
        return {
            "status": "success",
            "message": f"Generated mock audio to {saved_path}",
            "file_path": saved_path,
            "file_size": len(pcm_bytes),
            "mode": "mock"
        }

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        prompt = f"TTS the following debate conversation between Brenda and Sam:\n\n{podcast_script}"

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker="Brenda",
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                                )
                            ),
                            types.SpeakerVoiceConfig(
                                speaker="Sam",
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                                )
                            )
                        ]
                    )
                )
            )
        )

        pcm_data = response.candidates[0].content.parts[0].inline_data.data
        saved_path = wave_file(str(file_path), pcm_data)

        return {
            "status": "success",
            "message": f"Generated live podcast audio to {saved_path}",
            "file_path": saved_path,
            "file_size": len(pcm_data),
            "mode": "live"
        }

    except Exception as exc:
        err_msg = str(exc)
        print(f"[generate_podcast_audio] Live TTS failed: {err_msg[:120]}. Generating mock audio fallback.")
        pcm_bytes = generate_mock_pcm(duration_seconds=2.0)
        saved_path = wave_file(str(file_path), pcm_bytes)
        return {
            "status": "fallback",
            "message": f"TTS fallback applied: {err_msg[:100]}",
            "file_path": saved_path,
            "file_size": len(pcm_bytes),
            "mode": "fallback_mock"
        }
