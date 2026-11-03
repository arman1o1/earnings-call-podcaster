# AlphaCast Design Decisions Log

**Project**: AlphaCast — Autonomous Financial Earnings Call Debriefer  
**Directory**: `Projects/earnings-call-podcaster/`  
**Status**: Resolved  

---

## Decision Tree

| # | Decision | Depends on | Status | Choice | Why |
|---|---|---|---|---|---|
| 1 | Interaction Model: Live voice agent vs. CLI batch debriefer vs. Hybrid | — | resolved | Hybrid: CLI batch runner + ADK Web live voice | Enables rapid local automation and retains native live voice capabilities |
| 2 | Financial Data Ingestion Scope & Source Prioritization | #1 | resolved | yfinance + Google Search news with mock fallback | Reliable free data, grounded news, and robust offline testability |
| 3 | Podcast Debate Persona Dynamics & Duration | #1 | resolved | 2-min punchy Bull vs. Bear debate (Brenda/Kore vs. Sam/Puck) | Fast TTS synthesis, punchy audio, stays within Gemini TTS limits |
| 4 | Visual & Analytical Output Artifacts (Charts vs. MD only) | #2 | resolved | Audio WAV + Markdown Report + Matplotlib Charts (PNG) | Delivers complete multimodal package: audio, structured report, and visual EPS/price charts |
| 5 | Testing & API Mocking Architecture | #1, #2 | resolved | pytest with mock fixtures + opt-in live flag | Fast, deterministic offline verification without quota burn |
| 6 | Agent Framework & Orchestration Structure | — | resolved | Google ADK Coordinator + AgentTool | Standard architecture established in L4/L6 |
| 7 | Multi-Speaker TTS Engine & Voice Profiles | — | resolved | `gemini-2.5-flash-preview-tts` (Kore & Puck) | Native dual-speaker multi-turn PCM WAV output from L6 |
| 8 | Interceptor Safety & Provenance Mechanism | — | resolved | ADK `before_tool_callback` & `after_tool_callback` | Domain whitelist and process log injection from L5 |
| 9 | Data Serialization & Agent Contracts | — | resolved | Pydantic v2 `BaseModel` schemas | Typed handoff pattern from L6 |

---

## Shared Understanding
- **What's being built**: AlphaCast, an autonomous financial earnings call debriefer with a hybrid CLI and ADK Web live voice interface.
- **Target User**: Financial analysts, investors, and engineers seeking automated, multi-perspective spoken debriefs of corporate quarterly results.
- **Workflow**:
  1. User specifies a ticker (e.g. `NVDA`) and quarter either via CLI (`python run_cli.py --ticker NVDA`) or via live spoken audio in the ADK Web UI.
  2. The research agent pulls fundamentals via `yfinance` and live news via `google_search` (with fallback to local mock data fixtures if offline/rate-limited).
  3. Lifecycle callbacks (`before_tool_callback` and `after_tool_callback`) sanitize ticker inputs, filter low-credibility sources, and maintain provenance state.
  4. Extracted metrics are parsed into a validated Pydantic model (`EarningsReportSummary`).
  5. The podcast producer sub-agent scripts and synthesizes a punchy ~2-minute debate between Brenda (Bull / `Kore`) and Sam (Bear / `Puck`) using `gemini-2.5-flash-preview-tts`.
  6. Deliverables: 24 kHz WAV audio (`.wav`), structured Markdown briefing (`.md`), and matplotlib financial charts (`.png`).
- **Explicit Non-Goals**: Live trade execution, stock recommendation advice, real-time SEC filing parser for non-US equities.

---

## Assumptions
- **Audio Output Format**: 24 kHz 16-bit mono PCM WAV (standard for Gemini native TTS).
- **Environment**: Python 3.10+ with `google-adk`, `google-genai`, `yfinance`, `pydantic>=2.0`, `matplotlib`.
- **API Keys**: Uses standard `GEMINI_API_KEY` from root `.env` or local project `.env`.

---

## Top Risks & Mitigations
1. **Risk**: `yfinance` rate limiting or schema changes for newly reported earnings.  
   **Mitigation**: Defensive JSON error wrappers and built-in offline mock fixtures for popular tickers (e.g., NVDA, AAPL, MSFT, GOOGL).
2. **Risk**: Gemini TTS character budget or audio truncation during long scripts.  
   **Mitigation**: Strict Pydantic schema enforcing max dialogue turns (8–10 total exchanges, ~250–300 words total) to guarantee a tight 2-minute runtime.
3. **Risk**: Hallucinated financial numbers in the script vs. actual reported figures.  
   **Mitigation**: Direct schema injection where character dialogue prompts explicitly reference validated Pydantic metric fields.
