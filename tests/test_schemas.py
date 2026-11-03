import pytest
import sys
import pathlib

PROJECT_DIR = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from schemas import (
    EarningsMetrics,
    BullCase,
    BearCase,
    EarningsReportSummary,
    PodcastDialogueTurn,
    PodcastScript
)

def test_earnings_metrics_validation():
    metrics = EarningsMetrics(
        ticker="NVDA",
        quarter="Q3 FY2025",
        revenue="$35.08B",
        eps_actual=0.81,
        eps_estimate=0.75,
        eps_surprise_pct=8.0,
        stock_price="$145.89",
        price_change_pct=2.45,
        guidance_summary="Reaffirmed full year guidance."
    )
    assert metrics.ticker == "NVDA"
    assert metrics.eps_actual == 0.81
    assert metrics.eps_surprise_pct == 8.0

def test_podcast_script_tts_prompt_formatting():
    turns = [
        PodcastDialogueTurn(speaker="Brenda", text="Welcome everyone to the debrief."),
        PodcastDialogueTurn(speaker="Sam", text="Glad to be here, Brenda. Let's look at the numbers.")
    ]
    script = PodcastScript(
        title="Test Episode",
        ticker="AAPL",
        turns=turns
    )
    prompt = script.format_as_tts_prompt()
    assert "Brenda: Welcome everyone to the debrief." in prompt
    assert "Sam: Glad to be here, Brenda. Let's look at the numbers." in prompt

def test_earnings_report_summary_serialization():
    report = EarningsReportSummary(
        ticker="MSFT",
        quarter="Q1",
        executive_summary="Solid quarter driven by Azure cloud momentum.",
        metrics=EarningsMetrics(
            ticker="MSFT",
            revenue="$65.6B",
            eps_actual=3.30,
            eps_estimate=3.10,
            eps_surprise_pct=6.45,
            stock_price="$420.00",
            price_change_pct=1.8,
            guidance_summary="Cloud growth projected between 28-29%."
        ),
        bull_case=BullCase(
            analyst_name="Brenda",
            key_catalysts=["Azure AI acceleration", "Office 365 Copilot adoption"],
            topline_growth_highlight="Cloud revenue up 22% YoY",
            bull_thesis="Commercial cloud continues firing on all cylinders."
        ),
        bear_case=BearCase(
            analyst_name="Sam",
            key_risks=["Massive AI capex spend", "Data center capacity constraints"],
            valuation_headwind="CapEx run-rate exceeding $80B annually",
            bear_thesis="ROI timeline for enterprise generative AI remains unclear."
        ),
        process_log=["Verified via yfinance", "Grounded via Google Search"]
    )
    json_data = report.model_dump()
    assert json_data["ticker"] == "MSFT"
    assert len(json_data["process_log"]) == 2
    assert json_data["metrics"]["eps_actual"] == 3.30
