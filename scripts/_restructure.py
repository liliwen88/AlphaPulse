#!/usr/bin/env python3
"""
Automated restructuring script for AlphaPulse skill.
Creates new directory structure and files.
"""

import shutil
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BASE_DIRS = ["data", "core", "analysis", "reports", "reports/templates"]

def create_directories():
    """Create all necessary directories."""
    for dir_name in BASE_DIRS:
        dir_path = SCRIPT_DIR / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path.relative_to(SCRIPT_DIR.parent)}")

def create_init_files():
    """Create __init__.py files in all new directories."""
    init_content = {
        "data": '"""Data layer: Market data fetching, news aggregation, models, and configuration."""\n',
        "core": '"""Core analysis engine: Scoring and strategy generation."""\n',
        "analysis": '"""Analysis layer: Technical indicators and chart generation."""\n',
        "reports": '"""Reports layer: Report generation and formatting."""\n',
        "reports/templates": '"""Report templates for different output formats."""\n',
    }
    
    for dir_name, content in init_content.items():
        init_file = SCRIPT_DIR / dir_name / "__init__.py"
        init_file.write_text(content)
        print(f"✓ Created: {init_file.relative_to(SCRIPT_DIR.parent)}")

def create_terminology_file():
    """Create terminology mapping file."""
    content = '''"""Terminology mapping: Professional terms → Layman's language for reports."""

# Maps professional terms to simpler explanations
TERMINOLOGY_MAP = {
    # Technical Indicators
    "RSI": {
        "name": "相对强弱指数",
        "simple": "买卖热度",
        "explanation": "0-100的数值，表示股票被超买或超卖的程度。30以下说明卖方较强，70以上说明买方较强。"
    },
    "MACD": {
        "name": "MACD指标",
        "simple": "趋势动力",
        "explanation": "用来判断股价上升或下降趋势的强度。直方图为正表示上升动力，为负表示下降动力。"
    },
    "Bollinger Bands": {
        "name": "布林带",
        "simple": "波动范围",
        "explanation": "显示股价正常波动的上下界。如果价格触及上界可能高估，触及下界可能低估。"
    },
    "SMA": {
        "name": "移动平均线",
        "simple": "价格趋势",
        "explanation": "一段时间内的平均价格。如果价格在平均线上方，说明处于上升趋势；反之为下降趋势。"
    },
    "Volume": {
        "name": "成交量",
        "simple": "交易热度",
        "explanation": "一天内买卖的股票数量。成交量越大说明参与者越多，价格变动越有效。"
    },
    
    # Fundamental Terms
    "P/E Ratio": {
        "name": "市盈率",
        "simple": "估值倍数",
        "explanation": "股价相对每股收益的倍数。倍数越低可能越便宜，倍数越高可能越贵。"
    },
    "Market Cap": {
        "name": "市值",
        "simple": "公司规模",
        "explanation": "股价乘以总股数。数值越大说明公司越大越稳定。"
    },
    "Dividend Yield": {
        "name": "股息率",
        "simple": "红利收益率",
        "explanation": "每年分红相对股价的百分比。适合寻求稳定收益的投资者。"
    },
    
    # Price Levels
    "Support Level": {
        "name": "支撑位",
        "simple": "买入底线",
        "explanation": "历史低点附近的价格，股价常在此处反弹。"
    },
    "Resistance Level": {
        "name": "阻力位",
        "simple": "卖出顶线",
        "explanation": "历史高点附近的价格，股价常在此处回落。"
    },
    "Breakout": {
        "name": "突破",
        "simple": "向上爆发",
        "explanation": "股价突破之前的高点，通常预示着强势行情可能来临。"
    },
    "Breakdown": {
        "name": "跌破",
        "simple": "向下崩溃",
        "explanation": "股价跌破之前的低点，通常预示着弱势行情可能来临。"
    },
    
    # Sentiment
    "Bullish": {
        "name": "看涨",
        "simple": "看好（预期上升）",
        "explanation": "投资者预期股价会上升。"
    },
    "Bearish": {
        "name": "看跌",
        "simple": "看衰（预期下降）",
        "explanation": "投资者预期股价会下降。"
    },
    "Oversold": {
        "name": "超卖",
        "simple": "过度杀跌",
        "explanation": "股价被过度抛售，可能反弹。"
    },
    "Overbought": {
        "name": "超买",
        "simple": "过度追高",
        "explanation": "股价被过度追捧，可能回落。"
    },
    
    # Conviction/Confidence
    "High Conviction": {
        "name": "高信心",
        "simple": "强烈看好",
        "explanation": "多个分析维度都支持同一方向，信号明确。"
    },
    "Medium Conviction": {
        "name": "中等信心",
        "simple": "适度乐观",
        "explanation": "部分分析维度支持这个方向，但也有不确定因素。"
    },
    "Low Conviction": {
        "name": "低信心",
        "simple": "信号不明",
        "explanation": "分析维度混合矛盾，需要等待更多信号。"
    },
}

def get_simple_term(professional_term: str) -> str:
    """Get the simple layman's term for a professional term."""
    return TERMINOLOGY_MAP.get(professional_term, {}).get("simple", professional_term)

def get_explanation(professional_term: str) -> str:
    """Get explanation for a professional term."""
    return TERMINOLOGY_MAP.get(professional_term, {}).get("explanation", "")

def simplify_signal_text(text: str) -> str:
    """Replace professional terms in text with simple versions."""
    result = text
    for pro_term, mapping in TERMINOLOGY_MAP.items():
        simple = mapping.get("simple", pro_term)
        # Replace if found
        result = result.replace(pro_term, simple)
    return result
'''
    
    terminology_file = SCRIPT_DIR / "data" / "terminology.py"
    terminology_file.write_text(content)
    print(f"✓ Created: {terminology_file.relative_to(SCRIPT_DIR.parent)}")

def main():
    print("🔧 AlphaPulse Skill Restructuring")
    print("=" * 50)
    
    print("\n[1/3] Creating directories...")
    create_directories()
    
    print("\n[2/3] Creating __init__.py files...")
    create_init_files()
    
    print("\n[3/3] Creating terminology mapping...")
    create_terminology_file()
    
    print("\n" + "=" * 50)
    print("✅ Restructuring complete!")

if __name__ == "__main__":
    main()
