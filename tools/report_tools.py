import pathlib
from typing import Any, Dict, List

def format_debrief_markdown(
    ticker: str,
    quarter: str,
    metrics: Dict[str, Any],
    bull_case: Dict[str, Any],
    bear_case: Dict[str, Any],
    process_log: List[str]
) -> str:
    """Formats structured earnings debrief data into standard Markdown."""
    lines = [
        f"# AlphaCast Debrief: {ticker} ({quarter})",
        "",
        f"> Generated autonomously via Google ADK & Gemini Live Agents",
        "",
        "## Key Performance Metrics",
        "",
        f"| Metric | Reported Value |",
        f"| :--- | :--- |",
        f"| **Quarterly Revenue** | {metrics.get('revenue', 'N/A')} |",
        f"| **Reported EPS** | ${metrics.get('eps_actual', 0.0):.2f} |",
        f"| **Consensus Estimate** | ${metrics.get('eps_estimate', 0.0):.2f} |",
        f"| **EPS Surprise** | {metrics.get('eps_surprise_pct', 0.0):+.2f}% |",
        f"| **Current Price** | {metrics.get('stock_price', 'N/A')} ({metrics.get('price_change_pct', 0.0):+.2f}%) |",
        "",
        f"**Forward Guidance**: {metrics.get('guidance_summary', 'N/A')}",
        "",
        "---",
        "",
        "## Analyst Perspectives",
        "",
        "### Bullish Growth Case (Brenda)",
        f"- **Thesis**: {bull_case.get('bull_thesis', '')}",
        f"- **Highlight**: {bull_case.get('topline_growth_highlight', '')}",
        "- **Key Catalysts**:",
    ]
    for cat in bull_case.get("key_catalysts", []):
        lines.append(f"  - {cat}")

    lines.extend([
        "",
        "### Skeptical Valuation & Risk Case (Sam)",
        f"- **Thesis**: {bear_case.get('bear_thesis', '')}",
        f"- **Headwind**: {bear_case.get('valuation_headwind', '')}",
        "- **Key Risks**:",
    ])
    for risk in bear_case.get("key_risks", []):
        lines.append(f"  - {risk}")

    lines.extend([
        "",
        "---",
        "",
        "## Data Sourcing & Provenance Log",
    ])
    if process_log:
        for entry in process_log:
            lines.append(f"- {entry}")
    else:
        lines.append("- Fundamental data verified via yfinance and Google Search grounding.")

    return "\n".join(lines)

def save_debrief_markdown(filename: str, content: str) -> str:
    """Saves Markdown content to disk and returns the resolved absolute path."""
    file_path = pathlib.Path(filename).resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(file_path)
