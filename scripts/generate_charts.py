"""Generate candlestick and comparison charts using mplfinance and matplotlib."""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from config import DEFAULT_PERIOD, CHART_FIGSIZE, CHART_DPI, CHART_FORMAT, CHART_STYLE, YFINANCE_TIMEOUT


def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    """Get OHLCV data from yfinance."""
    stock = yf.Ticker(ticker)
    return stock.history(period=period, timeout=YFINANCE_TIMEOUT)


def generate_candlestick_chart(
    ticker: str,
    period: str,
    output_path: str,
    add_volume: bool = True,
    add_sma: bool = True,
) -> str:
    """Generate a single-ticker candlestick chart with overlays. Returns output_path."""
    history = fetch_history(ticker, period)
    if history.empty:
        raise ValueError(f"No price data for {ticker} (period={period})")

    addplots = []

    if add_sma:
        sma_20 = history["Close"].rolling(20).mean()
        sma_50 = history["Close"].rolling(50).mean()
        addplots.extend([
            mpf.make_addplot(sma_20, color="blue", width=0.8, label="SMA 20"),
            mpf.make_addplot(sma_50, color="orange", width=0.8, label="SMA 50"),
        ])

    style = mpf.make_mpf_style(base_mpf_style=CHART_STYLE)
    mpf.plot(
        history,
        type="candle",
        volume=add_volume,
        addplot=addplots,
        style=style,
        title=f"{ticker.upper()} — {period}",
        figsize=CHART_FIGSIZE,
        savefig=dict(fname=output_path, dpi=CHART_DPI),
    )
    plt.close("all")
    return output_path


def generate_comparison_chart(
    tickers: list[str],
    period: str,
    output_path: str,
) -> str:
    """Generate a normalized comparison chart (all rebased to 100). Returns output_path."""
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

    for ticker in tickers:
        try:
            history = fetch_history(ticker, period)
            if history.empty:
                print(f"Warning: No data for {ticker}", file=sys.stderr)
                continue
            normalized = history["Close"] / history["Close"].iloc[0] * 100
            ax.plot(history.index, normalized, label=ticker.upper(), linewidth=1.5)
        except Exception as e:
            print(f"Warning: Failed to fetch {ticker}: {e}", file=sys.stderr)

    ax.set_title(f"Normalized Comparison — {period}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Price (Base 100)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=CHART_DPI)
    plt.close(fig)
    return output_path


def generate_chart(
    ticker_or_tickers: str | list[str],
    period: str,
    chart_type: str,
    output_path: str,
) -> str:
    """Router: calls candlestick or comparison based on chart_type."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if chart_type == "comparison":
        tickers = ticker_or_tickers if isinstance(ticker_or_tickers, list) else [ticker_or_tickers]
        return generate_comparison_chart(tickers, period, output_path)
    else:
        ticker = ticker_or_tickers[0] if isinstance(ticker_or_tickers, list) else ticker_or_tickers
        return generate_candlestick_chart(ticker, period, output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate stock charts")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--period", "-p", default=DEFAULT_PERIOD, help="Data period (default: 6mo)")
    parser.add_argument("--type", "-t", choices=["candlestick", "comparison"], default="candlestick", help="Chart type")
    parser.add_argument("--compare", nargs="+", help="Comparison tickers (used with --type comparison)")
    parser.add_argument("--output", "-o", default="./chart.png", help="Output file path")
    args = parser.parse_args()

    tickers = [args.ticker] + (args.compare or []) if args.type == "comparison" else args.ticker

    try:
        output = generate_chart(tickers, args.period, args.type, args.output)
        print(f"Chart saved to {output}")
    except Exception as e:
        print(f"Error generating chart: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
