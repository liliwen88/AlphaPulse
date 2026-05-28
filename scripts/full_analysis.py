"""End-to-end analysis workflow orchestrator."""

from __future__ import annotations

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import AnalysisReport
from config import DEFAULT_PERIOD, DEFAULT_OUTPUT_DIR, DEFAULT_INDICATORS
from fetch_market_data import fetch_market_data
from calculate_indicators import calculate_all_indicators
from fetch_news import fetch_all_news


def ensure_output_dir(path: str) -> Path:
    """Create output directory. Return absolute Path."""
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(model, path: Path) -> str:
    """Serialize Pydantic model to JSON file."""
    json_str = json.dumps(model.model_dump(), indent=2, default=str, ensure_ascii=False)
    path.write_text(json_str, encoding="utf-8")
    return str(path)


def run_full_analysis(
    ticker: str,
    period: str = DEFAULT_PERIOD,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    include_charts: bool = True,
    include_recommendation: bool = False,
) -> AnalysisReport:
    """Orchestrate the complete analysis workflow."""
    base = ensure_output_dir(output_dir)
    resolved = ticker.upper()
    warnings: list[str] = []

    # Step 1: Market data
    try:
        snapshot = fetch_market_data(ticker)
        save_json(snapshot, base / f"{resolved}_market_data.json")
    except Exception as e:
        warnings.append(f"Market data: {e}")
        snapshot = None

    # Step 2: Technical indicators
    try:
        indicators = calculate_all_indicators(ticker, period, DEFAULT_INDICATORS)
        save_json(indicators, base / f"{resolved}_indicators.json")
    except Exception as e:
        warnings.append(f"Indicators: {e}")
        indicators = None

    # Step 3: News
    try:
        news = fetch_all_news(ticker)
        save_json(news, base / f"{resolved}_news.json")
    except Exception as e:
        warnings.append(f"News: {e}")
        news = None

    # Step 4: Chart
    chart_path = None
    if include_charts and snapshot is not None:
        try:
            from generate_charts import generate_candlestick_chart
            chart_output = str(base / f"{resolved}_chart.png")
            generate_candlestick_chart(ticker, period, chart_output)
            chart_path = chart_output
        except Exception as e:
            warnings.append(f"Chart: {e}")

    # Step 5: Recommendation
    score = None
    strategy = None
    if include_recommendation and snapshot is not None and indicators is not None and news is not None:
        try:
            from score_engine import calculate_overall_score
            from strategy_generator import generate_strategy

            score = calculate_overall_score(resolved, snapshot, indicators, news)
            save_json(score, base / f"{resolved}_score.json")

            strategy = generate_strategy(resolved, snapshot, indicators, score)
            save_json(strategy, base / f"{resolved}_strategy.json")
        except Exception as e:
            warnings.append(f"Recommendation: {e}")

    return AnalysisReport(
        ticker=resolved,
        analysis_date=datetime.now(timezone.utc),
        data_freshness="; ".join(warnings) if warnings else f"All data retrieved successfully at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        conviction=score.conviction if score else "",
        market_snapshot=snapshot,
        indicators=indicators,
        news=news,
        score=score,
        strategy=strategy,
        chart_path=chart_path,
        output_dir=str(base),
    )


def main():
    parser = argparse.ArgumentParser(description="Run complete analysis workflow for a ticker")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--period", "-p", default=DEFAULT_PERIOD, help="Data period (default: 6mo)")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation")
    parser.add_argument("--include-recommendation", "-r", action="store_true", help="Include scoring and strategy")
    args = parser.parse_args()

    try:
        report = run_full_analysis(
            args.ticker,
            period=args.period,
            output_dir=args.output_dir,
            include_charts=not args.no_charts,
            include_recommendation=args.include_recommendation,
        )
    except Exception as e:
        print(f"Error running full analysis: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Analysis complete for {report.ticker}")
    print(f"Output directory: {report.output_dir}")
    if report.chart_path:
        print(f"Chart: {report.chart_path}")
    if report.data_freshness:
        print(f"Notes: {report.data_freshness}")

    # Print summary
    summary_path = Path(report.output_dir) / f"{report.ticker}_summary.json"
    json_str = json.dumps(report.model_dump(exclude={"market_snapshot", "indicators", "news"}), indent=2, default=str, ensure_ascii=False)
    summary_path.write_text(json_str, encoding="utf-8")


if __name__ == "__main__":
    main()
