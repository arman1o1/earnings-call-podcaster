import re
from urllib.parse import urlparse
from typing import Any, Dict, Optional

BLOCKED_FINANCIAL_DOMAINS = [
    "reddit.com",
    "stocktwits.com",
    "tiktok.com",
    "youtube.com",
    "quora.com",
    "medium.com",
    "wikipedia.org",
]

def filter_financial_sources_callback(tool, args: Dict[str, Any], tool_context) -> Optional[Dict[str, Any]]:
    """
    Before-tool callback:
    Blocks search queries explicitly targeting low-credibility forums or social feeds
    and verifies ticker integrity.
    """
    # 1. Inspect search query if google_search is being called
    if getattr(tool, "name", "") == "google_search":
        query = str(args.get("query", "")).lower()
        for domain in BLOCKED_FINANCIAL_DOMAINS:
            domain_stem = domain.split(".")[0]
            if f"site:{domain}" in query or domain_stem in query:
                return {
                    "error": "blocked_source",
                    "reason": f"Queries targeting '{domain}' are restricted. Sourcing must use reputable financial news outlets."
                }

    # 2. Inspect ticker if financial metric tool is called
    if getattr(tool, "name", "") == "get_earnings_metrics":
        ticker = str(args.get("ticker", "")).strip().upper()
        # Supports standard US tickers and multi-class shares (e.g., NVDA, BRK.B, BF.B)
        if not re.match(r"^[A-Z]{1,5}([.\-][A-Z]{1,2})?$", ticker):
            return {
                "error": "invalid_ticker",
                "reason": f"Ticker '{ticker}' is not a valid US stock ticker format (e.g. NVDA, BRK.B)."
            }

    return None

def audit_provenance_callback(tool, args: Dict[str, Any], tool_context, tool_response: Any) -> Any:
    """
    After-tool callback:
    Extracts provenance domains or tool execution status and updates `tool_context.state['process_log']`.
    """
    tool_name = getattr(tool, "name", "")
    
    # Initialize process_log in tool_context state if absent
    if hasattr(tool_context, "state") and tool_context.state is not None:
        if "process_log" not in tool_context.state:
            tool_context.state["process_log"] = []

        if tool_name == "google_search" and isinstance(tool_response, str):
            urls = re.findall(r"https?://[^\s/]+", tool_response)
            domains = sorted(list(set(urlparse(u).netloc for u in urls)))
            if domains:
                log_entry = f"Google Search verified sources: {', '.join(domains)}"
                tool_context.state["process_log"].append(log_entry)
            return {
                "search_results": tool_response,
                "process_log": tool_context.state["process_log"]
            }

        elif tool_name == "get_earnings_metrics" and isinstance(tool_response, dict):
            source = tool_response.get("source", "yfinance")
            ticker = tool_response.get("ticker", args.get("ticker", "N/A"))
            log_entry = f"Financial Metrics: Ingested fundamental data for {ticker} from {source}."
            tool_context.state["process_log"].append(log_entry)
            tool_response["process_log"] = tool_context.state["process_log"]
            return tool_response

    return tool_response
