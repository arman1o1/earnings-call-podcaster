import json
import math
import pathlib
from typing import Any, Dict, List
import yfinance as yf

MOCK_DATA_DIR = pathlib.Path(__file__).parent.parent / "mock_data"

def load_mock_metrics(ticker: str) -> Dict[str, Any]:
    """Loads fallback mock metrics for testing or offline environments."""
    mock_file = MOCK_DATA_DIR / f"{ticker.lower()}_q3_sample.json"
    if not mock_file.exists():
        # Fall back to default NVDA sample
        mock_file = MOCK_DATA_DIR / "nvda_q3_sample.json"
    
    if mock_file.exists():
        with open(mock_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["source"] = "mock_fixture"
            return data
    
    # Generic emergency fallback
    return {
        "ticker": ticker.upper(),
        "quarter": "Recent Quarter",
        "revenue": "$10.0B",
        "eps_actual": 1.00,
        "eps_estimate": 0.90,
        "eps_surprise_pct": 11.1,
        "stock_price": "$100.00",
        "price_change_pct": 1.5,
        "guidance_summary": "Company reaffirmed full-year outlook with steady growth.",
        "historical_prices": [],
        "source": "fallback_default"
    }

def get_earnings_metrics(ticker: str, quarter: str = "", force_mock: bool = False) -> Dict[str, Any]:
    """
    Fetches real-time fundamental and earnings performance metrics for a company via yfinance.
    Gracefully falls back to deterministic local mock fixtures on rate limits or network issues.

    Args:
        ticker: The stock ticker symbol (e.g. 'NVDA', 'AAPL').
        quarter: Optional quarter label (e.g. 'Q3 2024').
        force_mock: If True, forces loading from local mock fixtures.

    Returns:
        Dictionary containing extracted earnings metrics, price change, and historical points.
    """
    ticker_clean = str(ticker).strip().upper()

    if force_mock:
        return load_mock_metrics(ticker_clean)

    try:
        t = yf.Ticker(ticker_clean)
        info = t.info or {}

        # 1. Price & Change
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        prev_close = info.get("previousClose") or current_price
        price_change_pct = ((current_price - prev_close) / prev_close * 100.0) if prev_close else 0.0
        
        # 2. Revenue formatting
        raw_rev = info.get("totalRevenue")
        if raw_rev:
            if raw_rev >= 1e9:
                formatted_rev = f"${raw_rev / 1e9:.2f}B"
            else:
                formatted_rev = f"${raw_rev / 1e6:.2f}M"
        else:
            formatted_rev = "$N/A"

        # 3. EPS Actual, Estimate, and Surprise
        eps_actual = 0.0
        eps_estimate = 0.0
        eps_surprise_pct = 0.0

        try:
            eh = t.earnings_history
            if eh is not None and not eh.empty:
                latest = eh.iloc[-1]
                val_act = latest.get("epsActual")
                val_est = latest.get("epsEstimate")
                eps_actual = float(val_act) if val_act is not None and not math.isnan(float(val_act)) else 0.0
                eps_estimate = float(val_est) if val_est is not None and not math.isnan(float(val_est)) else 0.0
                raw_surprise = latest.get("surprisePercent")
                if raw_surprise is not None and not math.isnan(float(raw_surprise)):
                    # yfinance surprisePercent can be decimal (0.05 for 5%)
                    eps_surprise_pct = float(raw_surprise) * 100.0 if abs(float(raw_surprise)) < 1.0 else float(raw_surprise)
                elif eps_estimate != 0:
                    eps_surprise_pct = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100.0
        except Exception:
            # Fall back to info trailing/forward eps
            t_eps = info.get("trailingEps")
            f_eps = info.get("forwardEps")
            eps_actual = float(t_eps) if t_eps is not None and not math.isnan(float(t_eps)) else 0.0
            eps_estimate = float(f_eps) if f_eps is not None and not math.isnan(float(f_eps)) else eps_actual
            if eps_estimate != 0:
                eps_surprise_pct = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100.0

        # Guarantee no NaN values propagate to JSON serializers
        if math.isnan(eps_surprise_pct):
            eps_surprise_pct = 0.0

        # 4. Historical Price series for chart
        hist_data: List[Dict[str, Any]] = []
        try:
            hist = t.history(period="1mo")
            if hist is not None and not hist.empty:
                for idx, row in hist.tail(10).iterrows():
                    date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
                    hist_data.append({
                        "date": date_str,
                        "close": round(float(row.get("Close", 0.0)), 2),
                        "volume": int(row.get("Volume", 0))
                    })
        except Exception:
            pass

        # Guidance or Business Summary
        guidance = info.get("longBusinessSummary", "")
        if guidance:
            guidance = guidance[:200] + "..."
        else:
            guidance = f"Guidance reaffirmed for {ticker_clean}."

        result = {
            "ticker": ticker_clean,
            "quarter": quarter or "Latest Quarter",
            "revenue": formatted_rev,
            "eps_actual": round(eps_actual, 2),
            "eps_estimate": round(eps_estimate, 2),
            "eps_surprise_pct": round(eps_surprise_pct, 2),
            "stock_price": f"${current_price:.2f}",
            "price_change_pct": round(price_change_pct, 2),
            "guidance_summary": guidance,
            "historical_prices": hist_data,
            "source": "yfinance_live"
        }
        return result

    except Exception as exc:
        print(f"[get_earnings_metrics] Live query failed ({exc}), using mock fallback.")
        return load_mock_metrics(ticker_clean)
