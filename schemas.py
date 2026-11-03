from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class EarningsMetrics(BaseModel):
    """Core financial metrics extracted for the earnings quarter."""
    ticker: str = Field(description="Company stock ticker symbol (e.g., 'NVDA').")
    quarter: str = Field(default="Q3", description="Quarter identifier (e.g., 'Q3 2024').")
    revenue: str = Field(description="Reported quarterly revenue (e.g., '$35.08B').")
    eps_actual: float = Field(description="Actual EPS reported (e.g., 0.81).")
    eps_estimate: float = Field(description="Consensus EPS estimate (e.g., 0.75).")
    eps_surprise_pct: float = Field(description="Percentage surprise: ((actual - estimate) / estimate) * 100.")
    stock_price: str = Field(description="Current stock price formatted, e.g., '$145.89'.")
    price_change_pct: float = Field(description="Stock price percentage change, e.g., 2.35.")
    guidance_summary: str = Field(description="Forward guidance overview or revenue forecast.")

class BullCase(BaseModel):
    """Bullish growth perspective presented by analyst Brenda."""
    analyst_name: str = Field(default="Brenda", description="Name of the bull-case host.")
    key_catalysts: List[str] = Field(description="Top 2-3 bullish drivers (e.g., data center demand, TAM expansion).")
    topline_growth_highlight: str = Field(description="Key growth metric or margin achievement.")
    bull_thesis: str = Field(description="2-3 sentence optimistic summary.")

class BearCase(BaseModel):
    """Skeptical valuation & risk perspective presented by analyst Sam."""
    analyst_name: str = Field(default="Sam", description="Name of the bear-case host.")
    key_risks: List[str] = Field(description="Top 2-3 risks (e.g., supply bottlenecks, margin deceleration, valuation).")
    valuation_headwind: str = Field(description="Key valuation or macroeconomic multiple concern.")
    bear_thesis: str = Field(description="2-3 sentence skeptic critique.")

class EarningsReportSummary(BaseModel):
    """Comprehensive structured earnings debrief report."""
    title: str = Field(default="AlphaCast Earnings Debrief", description="Title of the briefing.")
    ticker: str = Field(description="Company stock ticker.")
    quarter: str = Field(description="Reported quarter.")
    executive_summary: str = Field(description="Concise 2-sentence executive summary.")
    metrics: EarningsMetrics = Field(description="Parsed numerical metrics.")
    bull_case: BullCase = Field(description="Bull analysis.")
    bear_case: BearCase = Field(description="Bear critique.")
    process_log: List[str] = Field(default_factory=list, description="Audit provenance log of data sources and callbacks.")

class PodcastDialogueTurn(BaseModel):
    """A single spoken exchange in the podcast debate."""
    speaker: Literal["Brenda", "Sam"] = Field(description="The host speaking this line: Brenda (Bull) or Sam (Bear).")
    text: str = Field(description="Spoken dialogue text. Natural, spoken language without stage directions.")

class PodcastScript(BaseModel):
    """Complete script for the multi-speaker podcast episode."""
    title: str = Field(description="Podcast episode title.")
    ticker: str = Field(description="Covered company ticker.")
    turns: List[PodcastDialogueTurn] = Field(description="Ordered list of dialogue turns (target 8-10 turns, ~250-300 words).")
    estimated_duration_seconds: int = Field(default=120, description="Estimated duration in seconds.")

    def format_as_tts_prompt(self) -> str:
        """Converts structured turns into the prompt format expected by Gemini multi-speaker TTS."""
        lines = []
        for turn in self.turns:
            lines.append(f"{turn.speaker}: {turn.text}")
        return "\n\n".join(lines)
