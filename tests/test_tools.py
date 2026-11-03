import os
import pathlib
import sys
import wave
import pytest

PROJECT_DIR = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from tools.financial_tools import get_earnings_metrics, load_mock_metrics
from tools.callbacks import filter_financial_sources_callback, audit_provenance_callback
from tools.chart_tools import generate_earnings_chart
from tools.report_tools import save_debrief_markdown, format_debrief_markdown
from tools.audio_tools import generate_podcast_audio, wave_file

def test_mock_financial_metrics_loader():
    metrics = load_mock_metrics("NVDA")
    assert metrics["ticker"] == "NVDA"
    assert "revenue" in metrics
    assert metrics["eps_actual"] == 0.81
    assert metrics["source"] == "mock_fixture"

def test_get_earnings_metrics_force_mock():
    metrics = get_earnings_metrics("NVDA", force_mock=True)
    assert metrics["ticker"] == "NVDA"
    assert "eps_surprise_pct" in metrics
    assert isinstance(metrics["eps_surprise_pct"], (int, float))

def test_filter_financial_sources_callback():
    class DummyTool:
        name = "google_search"

    # Blocked query targeting Reddit
    res_blocked = filter_financial_sources_callback(DummyTool(), {"query": "NVDA earnings discussion reddit"}, None)
    assert res_blocked is not None
    assert res_blocked.get("error") == "blocked_source"

    # Allowed professional query
    res_allowed = filter_financial_sources_callback(DummyTool(), {"query": "NVDA Q3 earnings consensus Bloomberg Reuters"}, None)
    assert res_allowed is None

    # Ticker format check (supports multi-class tickers like BRK.B)
    class MetricTool:
        name = "get_earnings_metrics"

    assert filter_financial_sources_callback(MetricTool(), {"ticker": "NVDA"}, None) is None
    assert filter_financial_sources_callback(MetricTool(), {"ticker": "BRK.B"}, None) is None
    assert filter_financial_sources_callback(MetricTool(), {"ticker": "INVALID_TOOLONG"}, None) is not None

def test_audit_provenance_callback():
    class DummyTool:
        name = "google_search"

    class DummyContext:
        state = {}

    ctx = DummyContext()
    search_output = "According to https://cnbc.com/nvda and https://reuters.com/tech NVDA crushed expectations."
    res = audit_provenance_callback(DummyTool(), {"query": "NVDA earnings"}, ctx, search_output)
    
    assert isinstance(res, dict)
    assert "process_log" in res
    assert len(ctx.state["process_log"]) > 0
    assert "cnbc.com" in ctx.state["process_log"][0]

def test_generate_earnings_chart(tmp_path):
    mock_metrics = load_mock_metrics("NVDA")
    chart_file = tmp_path / "test_nvda_chart.png"
    result_path = generate_earnings_chart("NVDA", mock_metrics, str(chart_file))
    
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 1000  # Valid non-empty PNG

def test_save_debrief_markdown(tmp_path):
    md_file = tmp_path / "test_report.md"
    content = "# Test Report\n\nContent here."
    saved = save_debrief_markdown(str(md_file), content)
    assert os.path.exists(saved)
    with open(saved, "r", encoding="utf-8") as f:
        assert f.read() == content

def test_generate_podcast_audio_mock(tmp_path):
    wav_file = tmp_path / "test_podcast.wav"
    res = generate_podcast_audio("Brenda: Hello!\nSam: Hi Brenda!", filename=str(wav_file), force_mock=True)
    
    assert res["status"] == "success"
    assert os.path.exists(res["file_path"])
    
    # Verify WAV header
    with wave.open(res["file_path"], "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 24000
        assert wf.getsampwidth() == 2
        assert wf.getnframes() > 0
