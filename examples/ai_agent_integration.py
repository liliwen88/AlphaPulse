"""
AlphaPulse SDK — AI Agent Integration Demo

This example shows how any AI platform (Claude, ChatGPT, Gemini) can consume
AlphaPulse's structured analysis results as JSON for tool-based function calling.
"""

import asyncio
import json

from alphapulse import AlphaPulse, AlphaPulseConfig, AlphaPulseSync


# ── Example 1: Async usage (recommended for production) ──

async def analyze_single_stock_async():
    ap = AlphaPulse()

    # Get a real-time quote
    quote = await ap.quote.get("NVDA")
    print("[Quote as JSON for AI Agent]")
    print(quote.model_dump_json(indent=2))

    # Technical analysis
    tech = await ap.technical.analyze("NVDA", period="6mo")
    print(f"\n[Technical Posture] {tech.posture} — {tech.posture_detail}")


# ── Example 2: Sync usage (for simple scripts / non-async environments) ──

def analyze_single_stock_sync():
    ap = AlphaPulseSync()

    result = ap.quote.get("AAPL")
    print(f"AAPL: ${result.current_price} "
          f"({'UP' if result.change > 0 else 'DOWN'} {abs(result.change_percent):.2f}%)")
    print(f"Disclaimer present: {bool(result.disclaimer)}")


# ── Example 3: AI Agent Tool Definition (function calling pattern) ──

def get_stock_quote(symbol: str) -> str:
    """
    AI agent tool: Get real-time stock quote for a ticker symbol.

    Args:
        symbol: US stock ticker symbol (e.g., 'AAPL', 'NVDA', 'TSLA')

    Returns:
        JSON string with price, volume, market cap, P/E ratio, and mandatory risk disclaimer.
    """
    ap = AlphaPulseSync()
    result = ap.quote.get(symbol)
    return result.model_dump_json()


def get_technical_analysis(symbol: str) -> str:
    """
    AI agent tool: Get technical analysis summary for a ticker.

    Args:
        symbol: US stock ticker symbol.

    Returns:
        JSON string with moving averages, MACD, RSI, Bollinger Bands, support/resistance
        levels, volume profile, and overall posture.
    """
    ap = AlphaPulseSync()
    result = ap.technical.analyze(symbol)
    return result.model_dump_json()


def scan_market_hotspots() -> str:
    """
    AI agent tool: Scan broader market for sector rotation, top movers, and unusual volume.

    Returns:
        JSON string with index snapshots, sector performance, top gainers/losers,
        unusual volume alerts, and thematic basket performance.
    """
    ap = AlphaPulseSync()
    result = ap.hotspots.scan()
    return result.model_dump_json()


# ── Example 4: AI Agent function schema (Anthropic/OpenAI tool format) ──

TOOL_DEFINITIONS = [
    {
        "name": "get_stock_quote",
        "description": "Get real-time US stock quote with price, volume, market cap, P/E ratio.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "US stock ticker symbol (e.g., AAPL, NVDA, TSLA)",
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_technical_analysis",
        "description": "Get technical analysis indicators (SMA, MACD, RSI, Bollinger) for a stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "US stock ticker symbol"},
                "period": {
                    "type": "string",
                    "enum": ["1mo", "3mo", "6mo", "1y"],
                    "description": "Lookback period",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "scan_market_hotspots",
        "description": "Scan US market for sector rotation, top movers, unusual volume.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
]


if __name__ == "__main__":
    print("=" * 60)
    print("AlphaPulse AI Agent Integration Demo")
    print("=" * 60)

    # Sync example
    print("\n1. Sync Quote Example:")
    analyze_single_stock_sync()

    # Async example
    print("\n2. Async Analysis Example:")
    asyncio.run(analyze_single_stock_async())

    # Tool definitions
    print(f"\n3. AI Agent Tool Definitions: {len(TOOL_DEFINITIONS)} tools")
    for tool in TOOL_DEFINITIONS:
        print(f"   - {tool['name']}: {tool['description']}")

    print("\n4. Example tool call result:")
    result = get_stock_quote("TSLA")
    parsed = json.loads(result)
    print(f"   Ticker: {parsed['symbol']}")
    print(f"   Price: ${parsed['current_price']}")
    print(f"   P/E: {parsed.get('pe_ratio_ttm', 'N/A')}")
    print(f"   Has disclaimer: {'disclaimer' in parsed}")
