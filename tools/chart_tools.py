import pathlib
from typing import Any, Dict
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt

def generate_earnings_chart(ticker: str, metrics: Dict[str, Any], output_path: str) -> str:
    """
    Generates a dual-panel financial visualization:
    - Panel 1 (Left): EPS Estimate vs. Actual Bar Chart with surprise % badge.
    - Panel 2 (Right): Recent Stock Price Trend line chart.

    Args:
        ticker: Stock ticker symbol.
        metrics: Dictionary with EPS numbers, price change, and historical_prices.
        output_path: File path where PNG should be saved.

    Returns:
        Absolute path to the created PNG chart.
    """
    out_file = pathlib.Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=150)
    try:
        fig.patch.set_facecolor("#0e1117")

        for ax in (ax1, ax2):
            ax.set_facecolor("#161b22")
            ax.tick_params(colors="#c9d1d9", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("#30363d")

        # --- Panel 1: EPS Estimate vs Actual ---
        actual = metrics.get("eps_actual", 0.0)
        estimate = metrics.get("eps_estimate", 0.0)
        surprise_pct = metrics.get("eps_surprise_pct", 0.0)

        categories = ["Consensus\nEstimate", "Reported\nActual"]
        values = [estimate, actual]
        colors = ["#8b949e", "#2ea043" if actual >= estimate else "#da3633"]

        bars = ax1.bar(categories, values, color=colors, width=0.45, edgecolor="#ffffff", linewidth=0.8)
        for bar in bars:
            h = bar.get_height()
            ax1.annotate(f"${h:.2f}",
                         xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", va="bottom",
                         color="#ffffff", fontweight="bold", fontsize=10)

        sign = "+" if surprise_pct >= 0 else ""
        badge_color = "#238636" if surprise_pct >= 0 else "#da3633"
        ax1.set_title(f"{ticker} EPS Performance ({sign}{surprise_pct:.1f}% Surprise)",
                      color="#ffffff", fontsize=11, fontweight="bold", pad=12)
        ax1.set_ylabel("Earnings Per Share ($)", color="#c9d1d9", fontsize=9)
        ax1.grid(axis="y", linestyle="--", alpha=0.2, color="#8b949e")

        # --- Panel 2: Recent Price Trend ---
        hist_prices = metrics.get("historical_prices", [])
        if hist_prices:
            dates = [p["date"][-5:] for p in hist_prices]  # MM-DD
            closes = [p["close"] for p in hist_prices]
            line_color = "#58a6ff"
            ax2.plot(dates, closes, marker="o", color=line_color, linewidth=2, markersize=5)
            ax2.fill_between(dates, closes, min(closes) * 0.98, color=line_color, alpha=0.15)
            ax2.set_title(f"{ticker} 30-Day Price Trend ({metrics.get('stock_price', '')})",
                          color="#ffffff", fontsize=11, fontweight="bold", pad=12)
            ax2.set_ylabel("Closing Price ($)", color="#c9d1d9", fontsize=9)
            ax2.tick_params(axis="x", rotation=30)
            ax2.grid(True, linestyle="--", alpha=0.2, color="#8b949e")
        else:
            # Fallback single price display if no historical series
            cur_price = metrics.get("stock_price", "$N/A")
            chg = metrics.get("price_change_pct", 0.0)
            ax2.text(0.5, 0.5, f"Latest Price: {cur_price}\nDay Change: {chg:+.2f}%",
                     color="#ffffff", ha="center", va="center", fontsize=12, fontweight="bold")
            ax2.set_title(f"{ticker} Market Reaction", color="#ffffff", fontsize=11, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor="none")
        return str(out_file)
    finally:
        plt.close(fig)
