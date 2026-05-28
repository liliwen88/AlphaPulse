"""Fetch financial news from yfinance and web sources."""

import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yfinance as yf
import requests
from bs4 import BeautifulSoup
from models import NewsArticle, NewsBundle
from config import DEFAULT_NEWS_DAYS, DEFAULT_NEWS_SOURCES, MAX_ARTICLES_PER_SOURCE

BULLISH_WORDS = [
    "beat", "upgrade", "growth", "breakout", "surge", "rally", "raise",
    "outperform", "strong", "record", "profit", "buyback", "dividend",
    "approval", "launch", "partnership", "positive",
]
BEARISH_WORDS = [
    "miss", "downgrade", "decline", "investigation", "lawsuit", "crash",
    "plunge", "selloff", "cut", "underperform", "weak", "loss", "debt",
    "bankruptcy", "recall", "sanction", "tariff", "negative", "warning",
]


def fetch_yahoo_news(ticker: str) -> list[NewsArticle]:
    """Fetch news via yfinance's built-in .news property."""
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news
    except Exception:
        return []

    articles = []
    for item in raw_news[:MAX_ARTICLES_PER_SOURCE]:
        content = item.get("content", {})
        headline = content.get("title", "") or content.get("summary", "")[:100]
        summary = content.get("summary", "")
        pub_time = content.get("pubDate", "")
        url = content.get("canonicalUrl", {}).get("url", "")

        try:
            date = datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            date = datetime.now(timezone.utc)

        impact = assess_impact(headline, summary)
        articles.append(NewsArticle(
            headline=headline,
            date=date,
            source="Yahoo Finance",
            url=url or None,
            summary=summary[:300] if summary else None,
            impact=impact,
        ))

    return articles


def fetch_google_news(ticker: str, source_hint: str = "") -> list[NewsArticle]:
    """Fetch news via Google News RSS feed."""
    query = f"{ticker} stock"
    if source_hint and source_hint not in ("yahoo",):
        query = f"{ticker} {source_hint}"

    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US"
    articles = []

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:MAX_ARTICLES_PER_SOURCE]

        for item in items:
            title = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            pub_date_str = item.pubDate.text if item.pubDate else ""

            try:
                date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
            except (ValueError, AttributeError):
                date = datetime.now(timezone.utc)

            source_name = item.source.text if item.source else ("Google News" + (f" ({source_hint})" if source_hint else ""))
            impact = assess_impact(title, "")
            articles.append(NewsArticle(
                headline=title,
                date=date,
                source=source_name,
                url=link or None,
                impact=impact,
            ))
    except Exception:
        pass

    return articles


def assess_impact(headline: str, summary: str | None) -> str:
    """Heuristic keyword-based impact assessment."""
    text = (headline + " " + (summary or "")).lower()
    bullish_score = sum(1 for w in BULLISH_WORDS if w in text)
    bearish_score = sum(1 for w in BEARISH_WORDS if w in text)

    if bullish_score > bearish_score:
        return "Positive"
    if bearish_score > bullish_score:
        return "Negative"
    return "Neutral"


def filter_by_recency(articles: list[NewsArticle], max_days: int, fetched_at: datetime) -> list[NewsArticle]:
    """Remove articles older than max_days."""
    cutoff = fetched_at - timedelta(days=max_days)
    return [a for a in articles if a.date >= cutoff]


def fetch_all_news(ticker: str, days: int = DEFAULT_NEWS_DAYS, sources: list[str] | None = None) -> NewsBundle:
    """Orchestrate news fetching from all sources."""
    if sources is None:
        sources = DEFAULT_NEWS_SOURCES

    now = datetime.now(timezone.utc)
    bundle = NewsBundle(
        ticker=ticker.upper(),
        fetched_at=now,
        lookback_days=days,
        sources_attempted=list(sources),
    )

    all_articles: list[NewsArticle] = []

    for source in sources:
        source_lower = source.lower().strip()
        if source_lower == "yahoo":
            articles = fetch_yahoo_news(ticker)
        else:
            articles = fetch_google_news(ticker, source_hint=source_lower)

        if articles:
            bundle.sources_succeeded.append(source)

        all_articles.extend(articles)

    # Deduplicate by headline similarity
    seen_headlines: set[str] = set()
    unique_articles: list[NewsArticle] = []
    for article in all_articles:
        key = article.headline[:80].lower()
        if key not in seen_headlines:
            seen_headlines.add(key)
            unique_articles.append(article)

    bundle.articles = filter_by_recency(unique_articles, days, now)
    return bundle


def main():
    parser = argparse.ArgumentParser(description="Fetch financial news for a ticker")
    parser.add_argument("--ticker", "-t", required=True, help="Stock ticker symbol")
    parser.add_argument("--days", "-d", type=int, default=DEFAULT_NEWS_DAYS, help=f"Lookback days (default: {DEFAULT_NEWS_DAYS})")
    parser.add_argument("--sources", "-s", default=",".join(DEFAULT_NEWS_SOURCES), help="Comma-separated sources (default: reuters,bloomberg,yahoo)")
    parser.add_argument("--output", "-o", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    source_list = [s.strip() for s in args.sources.split(",")]

    try:
        bundle = fetch_all_news(args.ticker, args.days, source_list)
    except Exception as e:
        print(f"Error fetching news for {args.ticker}: {e}", file=sys.stderr)
        sys.exit(1)

    json_str = json.dumps(bundle.model_dump(), indent=2, default=str, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"News data saved to {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
