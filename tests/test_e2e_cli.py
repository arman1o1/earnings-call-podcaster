import os
import sys
import pathlib
import pytest

PROJECT_DIR = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from cli import run_alphacast_pipeline

def test_e2e_pipeline_mock(tmp_path):
    out_dir = tmp_path / "alphacast_out"
    res = run_alphacast_pipeline(
        ticker="NVDA",
        quarter="Q3 FY2025",
        force_mock=True,
        skip_audio=False,
        output_dir=str(out_dir)
    )

    assert res["ticker"] == "NVDA"
    assert os.path.exists(res["chart_path"])
    assert os.path.exists(res["report_path"])
    assert res["audio_path"] is not None
    assert os.path.exists(res["audio_path"])

    # Verify report content contains NVDA and Brenda/Sam
    with open(res["report_path"], "r", encoding="utf-8") as f:
        report_text = f.read()
        assert "AlphaCast Debrief: NVDA" in report_text
        assert "Brenda" in report_text
        assert "Sam" in report_text
        assert "EPS Surprise" in report_text
