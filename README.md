# AlphaCast: Autonomous Financial Earnings Call Debriefer

AlphaCast is an autonomous financial research and multi-speaker audio production system built with Google ADK (Agent Development Kit) and Gemini Live API models. It extracts quarterly corporate earnings performance, grounds reports using real-time Yahoo Finance metrics and news searches, validates data contracts with Pydantic, and produces an executive briefing package consisting of a Markdown report, a Matplotlib performance chart, and a synthesized two-speaker debate podcast featuring a bull-case analyst and a bear-case skeptic.

## Architecture

AlphaCast uses a hierarchical coordinator-specialist agent architecture:

```
                    +------------------------+
                    |    Root Coordinator    |
                    |   (AlphaCast Agent)    |
                    +-----------+------------+
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
+------------------------------+        +------------------------------+
|  Financial Research Agent    |        |    Podcast Producer Agent    |
|         (Sub-agent)          |        |    (AgentTool Specialist)    |
+------------------------------+        +------------------------------+
| * yfinance stock & EPS tools |        | * Dual-host debate script    |
| * Google Search news tool    |        | * Brenda (Bull / Kore)       |
| * Domain-filter callbacks    |        | * Sam (Bear / Puck)          |
| * Pydantic data schemas      |        | * gemini-2.5-flash-tts WAV   |
+------------------------------+        +------------------------------+
```

## Project Structure

```text
earnings-call-podcaster/
├── agents/
│   ├── podcast_agent.py      # Specialist sub-agent for multi-speaker TTS audio
│   └── root_agent.py         # Root coordinator managing research, charting, and debriefing
├── tools/
│   ├── audio_tools.py        # 24 kHz WAV audio serialization and Gemini TTS caller
│   ├── callbacks.py          # ADK before/after tool interceptors for source validation
│   ├── chart_tools.py        # Headless Matplotlib EPS comparison and price trend renderer
│   ├── financial_tools.py    # yfinance metric extractor with offline mock fallback
│   └── report_tools.py       # Executive Markdown report formatter and persistence
├── mock_data/
│   └── nvda_q3_sample.json   # Deterministic mock fixtures for offline testing
├── tests/
│   ├── test_schemas.py       # Pydantic schema validation tests
│   ├── test_tools.py         # Tools and interceptor unit tests
│   ├── test_e2e_cli.py       # End-to-end pipeline integration test
│   └── live_gemini_review.py # Live Gemini API validation test
├── agent.py                  # Standard Google ADK Web entrypoint
├── cli.py                    # Headless CLI entrypoint for batch execution
├── requirements.txt          # Pinned project dependencies
├── .env.example              # Environment configuration template
└── README.md                 # Project documentation
```

## Setup

1. **Clone and Navigate**:
   ```bash
   cd Projects/earnings-call-podcaster
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   Add your Google Gemini API key to `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### 1. Headless CLI Runner
Execute the complete analysis, report drafting, chart rendering, and podcast audio generation:

```bash
# Run with live Yahoo Finance and Gemini TTS for NVDA
python cli.py --ticker NVDA

# Run offline using mock fixtures (zero API quota consumption)
python cli.py --ticker NVDA --mock

# Run without audio generation (produces chart and report only)
python cli.py --ticker AAPL --no-audio

# Specify custom output directory
python cli.py --ticker GOOGL --output-dir my_reports
```

Generated outputs will be saved in the designated output folder:
- `{ticker}_debrief.md`: Structured executive debrief report
- `{ticker}_chart.png`: Dual-pane EPS surprise and price chart
- `{ticker}_podcast.wav`: 24 kHz 16-bit mono dual-speaker podcast audio

### 2. Interactive Voice Agent (ADK Web)
Launch the bidirectional live audio interface:

```bash
adk web --host 0.0.0.0 --port 8005
```
Open `http://localhost:8005` in your browser to speak directly with AlphaCast.

## Testing

Run the automated test suite:

```bash
pytest tests/ -v
```

To run the live Gemini API connectivity and TTS generation verification:

```bash
python tests/live_gemini_review.py
```
