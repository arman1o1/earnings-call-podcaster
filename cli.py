import argparse
import os
import sys
import pathlib
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv

# Load environment
load_dotenv(find_dotenv())

# Add project root to sys.path
PROJECT_DIR = pathlib.Path(__file__).parent.resolve()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from schemas import EarningsReportSummary, BullCase, BearCase, EarningsMetrics, PodcastDialogueTurn, PodcastScript
from tools.financial_tools import get_earnings_metrics
from tools.chart_tools import generate_earnings_chart
from tools.report_tools import format_debrief_markdown, save_debrief_markdown
from tools.audio_tools import generate_podcast_audio

def run_alphacast_pipeline(
    ticker: str,
    quarter: str = "",
    force_mock: bool = False,
    skip_audio: bool = False,
    output_dir: str = "output"
) -> Dict[str, Any]:
    """
    Executes the complete AlphaCast earnings debrief pipeline.
    """
    ticker_clean = ticker.strip().upper()
    out_dir = pathlib.Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[AlphaCast] 🎙️ Starting earnings debrief pipeline for {ticker_clean}...")

    # 1. Financial Metrics Ingestion
    print(f"[AlphaCast] 📊 Ingesting fundamental metrics (mode: {'MOCK' if force_mock else 'LIVE'})...")
    metrics_data = get_earnings_metrics(ticker=ticker_clean, quarter=quarter, force_mock=force_mock)
    
    # 2. Bull and Bear Perspectives
    bull_data = metrics_data.get("bull_case")
    bear_data = metrics_data.get("bear_case")

    if not bull_data or not bear_data:
        # Default synthesized perspectives based on metrics
        surprise = metrics_data.get("eps_surprise_pct", 0.0)
        direction = "outperformed" if surprise >= 0 else "missed"
        bull_data = {
            "analyst_name": "Brenda",
            "key_catalysts": [
                f"Quarterly revenue reached {metrics_data.get('revenue', 'N/A')}",
                f"EPS {direction} consensus expectations by {abs(surprise):.1f}%",
                "Robust enterprise demand and long-term operating leverage"
            ],
            "topline_growth_highlight": f"Strong execution with {metrics_data.get('stock_price', '')} market reaction",
            "bull_thesis": f"{ticker_clean} demonstrated resilient operational discipline this quarter. Strong structural fundamentals position the company well for sustained secular growth."
        }
        bear_data = {
            "analyst_name": "Sam",
            "key_risks": [
                "Elevated valuation multiples in a higher-for-longer macro interest rate environment",
                "Customer spending concentration and lengthening enterprise sales cycles",
                "Sequential gross margin pressures and rising operating expenditures"
            ],
            "valuation_headwind": "Rich multiples leave little margin for execution slip-ups",
            "bear_thesis": f"While headline numbers appear healthy, underlying margin dynamics warrant caution. At current price levels, future growth is already aggressively priced in."
        }

    # 3. Generate Visual Chart
    chart_file = out_dir / f"{ticker_clean.lower()}_chart.png"
    print(f"[AlphaCast] 📈 Rendering dual-pane performance chart...")
    chart_path = generate_earnings_chart(ticker=ticker_clean, metrics=metrics_data, output_path=str(chart_file))

    # 4. Save Markdown Debrief Report
    md_file = out_dir / f"{ticker_clean.lower()}_debrief.md"
    print(f"[AlphaCast] 📝 Writing executive debrief report...")
    md_content = format_debrief_markdown(
        ticker=ticker_clean,
        quarter=metrics_data.get("quarter", "Q3"),
        metrics=metrics_data,
        bull_case=bull_data,
        bear_case=bear_data,
        process_log=metrics_data.get("process_log", [f"Sourced via {metrics_data.get('source', 'yfinance')}."])
    )
    report_path = save_debrief_markdown(filename=str(md_file), content=md_content)

    # 5. Build Podcast Debate Script
    print(f"[AlphaCast] 🎭 Formulating dual-host debate script between Brenda and Sam...")
    script_turns = [
        PodcastDialogueTurn(speaker="Brenda", text=f"Welcome to AlphaCast! Today we are dissecting {ticker_clean}'s latest quarterly numbers. Sam, they reported revenue of {metrics_data.get('revenue', 'N/A')} and beat EPS expectations by {metrics_data.get('eps_surprise_pct', 0.0):.1f} percent. The bulls are celebrating!"),
        PodcastDialogueTurn(speaker="Sam", text=f"Hold your horses, Brenda. Yes, the headline beat looks shiny, but look at the valuation. Trading at current multiples leaves zero room for error if macro headwinds intensify."),
        PodcastDialogueTurn(speaker="Brenda", text=f"Come on, Sam. Look at the structural demand drivers. Topline numbers are accelerating and enterprise adoption continues to outpace expectations."),
        PodcastDialogueTurn(speaker="Sam", text=f"Demand is fine today, Brenda, but customer concentration and margin compression are real risks. If their largest buyers tap the brakes on capex, this stock will feel the squeeze."),
        PodcastDialogueTurn(speaker="Brenda", text=f"Their forward guidance proves the pipeline is as strong as ever. Investors with a multi-year horizon shouldn't get shaken out by short-term noise."),
        PodcastDialogueTurn(speaker="Sam", text=f"Fair point on the long term, Brenda, but disciplined capital allocators wait for a better margin of safety. That's a wrap on {ticker_clean}. Join us next quarter on AlphaCast!")
    ]
    script = PodcastScript(
        title=f"AlphaCast Debate: {ticker_clean} Earnings",
        ticker=ticker_clean,
        turns=script_turns
    )

    # 6. Synthesize Multi-Speaker Podcast
    audio_path = None
    if not skip_audio:
        print(f"[AlphaCast] 🔊 Synthesizing multi-speaker podcast audio via Gemini TTS...")
        audio_file = out_dir / f"{ticker_clean.lower()}_podcast.wav"
        tts_prompt = script.format_as_tts_prompt()
        audio_res = generate_podcast_audio(
            podcast_script=tts_prompt,
            filename=str(audio_file),
            force_mock=force_mock
        )
        audio_path = audio_res.get("file_path")
        print(f"[AlphaCast] ✅ Audio generated: {audio_path} ({audio_res.get('file_size', 0)} bytes)")
    else:
        print(f"[AlphaCast] ⏭️ Skipping audio generation (--no-audio).")

    print(f"\n[AlphaCast] 🚀 Complete! Generated artifacts:")
    print(f"  • Chart:  {chart_path}")
    print(f"  • Report: {report_path}")
    if audio_path:
        print(f"  • Audio:  {audio_path}")

    return {
        "ticker": ticker_clean,
        "metrics": metrics_data,
        "chart_path": chart_path,
        "report_path": report_path,
        "audio_path": audio_path
    }

def main():
    parser = argparse.ArgumentParser(description="AlphaCast: Autonomous Financial Earnings Debriefer")
    parser.add_argument("--ticker", "-t", type=str, default="NVDA", help="Stock ticker symbol (e.g. NVDA, AAPL)")
    parser.add_argument("--quarter", "-q", type=str, default="Q3", help="Quarter label (e.g. Q3 2024)")
    parser.add_argument("--mock", action="store_true", help="Use local deterministic mock data fixtures")
    parser.add_argument("--no-audio", action="store_true", help="Skip Gemini TTS audio generation")
    parser.add_argument("--output-dir", "-o", type=str, default="output", help="Directory to save generated outputs")

    args = parser.parse_args()
    run_alphacast_pipeline(
        ticker=args.ticker,
        quarter=args.quarter,
        force_mock=args.mock,
        skip_audio=args.no_audio,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()
