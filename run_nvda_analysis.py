
import os
import sys
os.environ["YFINANCE_CACHE_ENABLED"] = "False"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from datetime import datetime, timezone

print("="*60)
print("NVIDIA (NVDA) 完整分析")
print("="*60)
print(f"开始时间: {datetime.now(timezone.utc)} UTC\n")

try:
    from fetch_market_data import fetch_market_data
    from calculate_indicators import calculate_all_indicators
    from fetch_news import fetch_all_news
    from score_engine import calculate_overall_score
    from strategy_generator import generate_strategy
    from config import DEFAULT_PERIOD, DEFAULT_INDICATORS
    
    print("[1/5] 获取市场数据...")
    snapshot = fetch_market_data("NVDA")
    print(f"  ✓ 当前价格: ${snapshot.current_price:.2f}")
    print(f"  ✓ 市值: ${snapshot.market_cap/1e9:.1f}B" if snapshot.market_cap else "  ✓ 市值: N/A")
    
    print("\n[2/5] 计算技术指标...")
    indicators = calculate_all_indicators("NVDA", DEFAULT_PERIOD, DEFAULT_INDICATORS)
    print(f"  ✓ RSI(14): {indicators.rsi:.1f}" if indicators.rsi else "  ✓ RSI: N/A")
    print(f"  ✓ MACD: {indicators.macd:.4f}" if indicators.macd else "  ✓ MACD: N/A")
    
    print("\n[3/5] 获取新闻...")
    news = fetch_all_news("NVDA")
    print(f"  ✓ 新闻条数: {len(news.articles)}")
    
    print("\n[4/5] 综合评分...")
    score = calculate_overall_score("NVDA", snapshot, indicators, news)
    print(f"  ✓ 总评分: {score.overall_score:.1f}/100")
    print(f"  ✓ 信念级别: {score.conviction}")
    
    print("\n[5/5] 生成策略...")
    strategy = generate_strategy("NVDA", snapshot, indicators, score)
    print(f"  ✓ 信号: {strategy.signal}")
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)
    
    print("\n--- 详细信息 ---")
    print(f"\n市场数据:")
    print(f"  今日变动: {snapshot.day_change_pct:+.2f}%")
    print(f"  成交量: {snapshot.volume/1e6:.1f}M (vs平均: {snapshot.avg_volume/1e6:.1f}M)")
    print(f"  52周区间: ${snapshot.fifty_two_week_low:.2f} - ${snapshot.fifty_two_week_high:.2f}")
    print(f"  当前位置: {snapshot.fifty_two_week_position_pct:.0f}%")
    
    print(f"\n技术指标:")
    print(f"  RSI: {indicators.rsi:.1f} - {'超卖' if indicators.rsi and indicators.rsi < 30 else '超买' if indicators.rsi and indicators.rsi > 70 else '中性'}")
    print(f"  MACD: {indicators.macd:.4f}, Histogram: {indicators.macd_histogram:.4f} - {'看涨' if indicators.macd_histogram and indicators.macd_histogram > 0 else '看跌' if indicators.macd_histogram and indicators.macd_histogram < 0 else '中性'}")
    print(f"  SMA20: ${indicators.sma_20:.2f}" if indicators.sma_20 else "  SMA20: N/A")
    print(f"  SMA50: ${indicators.sma_50:.2f}" if indicators.sma_50 else "  SMA50: N/A")
    
    print(f"\n投资策略:")
    print(f"  信号: {strategy.signal}")
    if strategy.entry_price:
        print(f"  入场价: ${strategy.entry_price:.2f}")
    if strategy.take_profit:
        print(f"  止盈价: ${strategy.take_profit:.2f}")
    print(f"  止损价: ${strategy.stop_loss:.2f}")
    print(f"  建议仓位: {strategy.position_size_pct:.0f}%")
    print(f"  理由: {strategy.rationale}")
    
    print(f"\n综合评分详情:")
    for dim in score.dimensions:
        print(f"  {dim.dimension.capitalize()}: {dim.raw_score:.1f} (权重: {dim.weight*100:.0f}%)")
    
    print(f"\n近期新闻 (前3条):")
    for i, article in enumerate(news.articles[:3], 1):
        impact_emoji = {"Positive": "📈", "Negative": "📉", "Neutral": "➡️"}.get(article.impact, "➡️")
        print(f"  {i}. [{article.date.strftime('%Y-%m-%d')}] {impact_emoji} {article.headline}")
    
    print("\n" + "="*60)
    print("⚠️ 免责声明: 本分析仅供信息参考，不构成投资建议。")
    print("   投资涉及风险，请自行研究并咨询专业人士。")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

