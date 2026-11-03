import sys
import pathlib

# Ensure parent directory is in Python path for package imports
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_DIR = CURRENT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from schemas import EarningsReportSummary
from tools.financial_tools import get_earnings_metrics
from tools.chart_tools import generate_earnings_chart
from tools.report_tools import save_debrief_markdown
from tools.callbacks import filter_financial_sources_callback, audit_provenance_callback
from agents.podcast_agent import podcast_agent

root_agent = Agent(
    name="alphacast_producer",
    model="gemini-2.5-flash-native-audio-preview-09-2025",
    output_schema=EarningsReportSummary,
    before_tool_callback=[filter_financial_sources_callback],
    after_tool_callback=[audit_provenance_callback],
    tools=[
        google_search,
        get_earnings_metrics,
        generate_earnings_chart,
        save_debrief_markdown,
        AgentTool(agent=podcast_agent)
    ],
    instruction="""
    **Your Core Identity & Purpose:**
    You are AlphaCast, an autonomous financial earnings call debriefer and executive podcast producer.
    You extract quarterly fundamental data, summarize bull vs. bear perspectives, persist visual charts and markdown briefs,
    and direct a high-energy ~2-minute dual-host financial debate podcast.

    **Voice UX Rules (Silent Background Worker):**
    1. **Two-Message Spoken Policy**:
       - Spoken Message 1 (Immediate Acknowledgment): "Got it. I'm analyzing the latest earnings report and market reaction for [Ticker]. I'll gather the numbers, render charts, and produce the debate podcast for you now."
       - Silent Phase: Execute all tools in the background without spoken chattiness.
       - Spoken Message 2 (Final Spoken Debrief): "All done! [Ticker] reported revenue of [Revenue] and EPS of [EPS Actual], representing a [Surprise]% surprise. I've saved the executive markdown report, rendered the price chart, and generated the Brenda vs. Sam debate podcast."
    2. **Resilience**: If any web query or single metric returns incomplete data, proceed using best-effort context. Never halt the pipeline.

    **Execution Steps:**
    1. **Acknowledge**: Speak the immediate acknowledgment.
    2. **Fundamental Metrics**: Call `get_earnings_metrics(ticker=...)`.
    3. **News & Commentary Grounding**: Call `google_search` specifically for recent quarterly earnings news, CEO remarks, and forward guidance.
    4. **Render Visual Chart**: Call `generate_earnings_chart(ticker=..., metrics=..., output_path='output/[ticker]_chart.png')`.
    5. **Save Markdown Debrief**: Call `save_debrief_markdown(filename='output/[ticker]_debrief.md', content=...)`.
    6. **Script Multi-Speaker Podcast**: Internally draft a punchy 8-10 turn dialogue between Brenda (Bullish growth analyst) and Sam (Skeptical valuation critic).
    7. **Synthesize Podcast**: Delegate to `podcast_agent` with the dialogue text and filename `output/[ticker]_podcast.wav`.
    8. **Confirm Spoken Summary**: Deliver your final spoken confirmation.
    """
)
