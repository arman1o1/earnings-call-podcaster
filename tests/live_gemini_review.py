import os
import sys
import pathlib
import wave
from dotenv import load_dotenv, find_dotenv

# Load root or local .env
load_dotenv(find_dotenv())

PROJECT_DIR = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from google import genai
from google.genai import types
from cli import run_alphacast_pipeline
from tools.audio_tools import generate_podcast_audio

def run_live_gemini_review():
    print("=" * 60)
    print("🌟 RUNNING LIVE GEMINI API REVIEW FOR ALPHACAST")
    print("=" * 60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment.")
        return False

    print(f"✅ GEMINI_API_KEY detected (Prefix: {api_key[:8]}...)")
    client = genai.Client(api_key=api_key)

    # 1. Test text model connectivity (gemini-2.5-flash)
    print("\n--- Test 1: Gemini 2.5 Flash Text & Reasoning ---")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'AlphaCast system online' and provide one sentence summarizing why multi-speaker TTS is impactful for financial briefings."
        )
        print(f"Model Response:\n{response.text.strip()}")
        print("✅ Gemini 2.5 Flash text generation succeeded.")
    except Exception as e:
        print(f"❌ Gemini text call failed: {e}")
        return False

    # 2. Test Multi-Speaker TTS model (gemini-2.5-flash-preview-tts)
    print("\n--- Test 2: Gemini 2.5 Flash Preview TTS Multi-Speaker Synthesis ---")
    test_audio_path = PROJECT_DIR / "output" / "live_tts_review.wav"
    sample_dialogue = (
        "Brenda: Nvidia just beat estimates by eight percent, Sam! The AI infrastructure cycle is roaring.\n\n"
        "Sam: Eight percent is solid, Brenda, but trading at fifty times forward earnings leaves no room for any supply bottlenecks."
    )
    
    try:
        audio_res = generate_podcast_audio(
            podcast_script=sample_dialogue,
            filename=str(test_audio_path),
            force_mock=False
        )
        print(f"Audio result status: {audio_res.get('status')}")
        print(f"Audio file: {audio_res.get('file_path')} ({audio_res.get('file_size')} bytes)")
        
        # Verify WAV integrity
        with wave.open(audio_res["file_path"], "rb") as wf:
            channels = wf.getnchannels()
            rate = wf.getframerate()
            frames = wf.getnframes()
            duration = frames / float(rate)
            print(f"Audio properties: {channels} channel(s), {rate} Hz, {duration:.2f} seconds")
            assert channels == 1
            assert rate == 24000
            assert duration > 1.0

        print("✅ Gemini Multi-Speaker TTS synthesis succeeded.")
    except Exception as e:
        print(f"❌ Gemini TTS synthesis failed: {e}")
        return False

    # 3. Test Full Pipeline with Live yfinance data & Gemini TTS
    print("\n--- Test 3: End-to-End Pipeline Execution (Live NVDA) ---")
    try:
        out_dir = PROJECT_DIR / "output"
        res = run_alphacast_pipeline(
            ticker="NVDA",
            quarter="Q3 FY2025",
            force_mock=False,
            skip_audio=False,
            output_dir=str(out_dir)
        )
        print(f"Pipeline executed successfully for {res['ticker']}:")
        print(f"  Chart: {res['chart_path']}")
        print(f"  Report: {res['report_path']}")
        print(f"  Podcast Audio: {res['audio_path']}")
        print("✅ End-to-end AlphaCast live pipeline validated.")
    except Exception as e:
        print(f"❌ Live pipeline failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 ALL REAL GEMINI API REVIEWS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_live_gemini_review()
    sys.exit(0 if success else 1)
