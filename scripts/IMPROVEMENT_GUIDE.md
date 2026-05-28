# AlphaPulse Skill 改进说明

## 📋 新增功能概览

AlphaPulse skill 已进行重大改进，旨在为普通投资者提供**更清晰**、**更可操作**的投资分析。

### 主要改进

#### 1️⃣ **投资决策卡** (Decision Card)
新增了**结构化投资决策卡**，提供清晰的买入/卖出信号和价格目标：

```
📊 NVDA 投资决策卡
┌─────────────────────────────────┐
│ 信号: 📈 BUY                    │
│ 信心度: 🔴 High                 │
├─────────────────────────────────┤
│ 目标价格: $150 - $170           │
│ 推荐入场价: $145                 │
│ 止损价(风险): $140              │
│ 止盈价(收益): $165              │
├─────────────────────────────────┤
│ 概率评估:                       │
│ 📈 上升: 70%  📉 下跌: 20%     │
│ ➡️ 盘整: 10%                   │
└─────────────────────────────────┘
```

#### 2️⃣ **通俗易懂的简化报告** (Simple Report)
使用了大量的**图表符号**和**白话解释**，让非专业投资者能快速理解：

- 🔴 🟡 🟢 信心等级
- 📈 📉 ➡️ 方向指示
- 明确的"买入底线"、"卖出顶线"等通俗说法
- 每个技术指标后都有"简单理解"说明

#### 3️⃣ **术语转换表** (Terminology Mapping)
建立了专业术语到通俗语言的映射，包括：

| 专业术语 | 通俗说法 | 简单理解 |
|--------|--------|--------|
| RSI | 相对强弱指数 | 买卖热度 |
| MACD | MACD指标 | 趋势动力 |
| Bollinger Bands | 布林带 | 波动范围 |
| P/E Ratio | 市盈率 | 估值倍数 |
| Support Level | 支撑位 | 买入底线 |

#### 4️⃣ **明确的投资策略** (Clear Strategy)
生成的报告包含明确的：
- ✅ 建议行动 (BUY/SELL/HOLD)
- ✅ 具体价格 (入场价、止损、止盈、目标价)
- ✅ 成功概率 (向上/向下/盘整)
- ✅ 主要看点 (什么会改变观点)
- ✅ 风险提示 (需要警惕的事项)

---

## 🚀 使用方式

### 基础用法
```bash
# 生成简化版报告(推荐给普通投资者)
python investment_advisor.py NVDA --format simple

# 生成专业版报告(详细分析)
python investment_advisor.py NVDA --format md

# 生成JSON数据(供其他系统使用)
python investment_advisor.py NVDA --format json
```

### 高级选项
```bash
# 指定时间框架
python investment_advisor.py NVDA --format simple --timeframe short  # 1个月
python investment_advisor.py NVDA --format simple --timeframe medium # 6个月(默认)
python investment_advisor.py NVDA --format simple --timeframe long   # 1年

# 指定数据周期
python investment_advisor.py NVDA --format simple --period 3mo

# 指定输出文件
python investment_advisor.py NVDA --format simple --output ./analysis/nvda_analysis.md
```

---

## 📁 新的目录结构

已按照通用skill标准重组目录：

```
scripts/
├── core/                          # 核心分析引擎
│   ├── __init__.py
│   ├── score_engine.py           # 多维评分（技术+基本面+新闻+情绪+宏观）
│   └── strategy_generator.py      # 策略生成
│
├── data/                          # 数据层
│   ├── __init__.py
│   ├── models.py                 # 数据模型
│   ├── fetch_market_data.py      # 市场数据获取
│   ├── fetch_news.py             # 新闻聚合
│   ├── config.py                 # 配置常量
│   └── terminology.py            # 术语转换表 ⭐ NEW
│
├── analysis/                      # 分析工具
│   ├── __init__.py
│   ├── calculate_indicators.py   # 技术指标计算
│   └── generate_charts.py        # 图表生成
│
├── reports/                       # 报告生成
│   ├── __init__.py
│   ├── report_generator.py       # 统一报告生成 ⭐ PLANNED
│   └── templates/                # 报告模板
│       └── __init__.py
│
├── decision_card.py              # 投资决策卡类 ⭐ NEW
├── decision_card_generator.py    # 决策卡生成器 ⭐ NEW
├── simple_report_generator.py    # 简化报告生成器 ⭐ NEW
├── terminology.py                # 术语映射 ⭐ NEW
├── investment_advisor.py         # 主入口（已改进）✓ UPDATED
├── full_analysis.py              # 完整分析（保留）
├── requirements.txt
└── README.md                     # 本文件
```

---

## 🎯 报告格式对比

### 简化版 (format=simple) - 普通投资者适用
✅ 彩色符号和图表  
✅ 白话解释和简化术语  
✅ 明确的买/卖/持信号  
✅ 具体的价格和行动步骤  
✅ 一眼看懂的概率评估  

**使用场景**: 股民自己分析、给家人朋友解释、微信/邮件分享

### 专业版 (format=md) - 财务分析师适用
✅ 详细的技术指标分析  
✅ 基本面和宏观背景  
✅ 完整的新闻总结  
✅ 多维度评分展示  
✅ 专业术语保留  

**使用场景**: 深度分析、研究报告、机构投资者

### JSON格式 (format=json) - 数据集成
✅ 结构化数据  
✅ 可被其他系统解析  
✅ 便于统计分析  

**使用场景**: API集成、自动化分析、数据库存储

---

## 📊 简化报告示例

### 速览
```
⚡ 投资建议
📈 推荐买入 - 现在是不错的买点

信心评级: 🔴 强烈看好 - 信号非常明确
```

### 白话分析
```
💡 简单分析说明
- 买卖热度: 热度适中，市场情绪稳定
- 新闻面: 最近有不少积极消息，看好因素较多
```

### 价格目标
```
🎯 价格目标
- 推荐入场价: $145.50
- 目标价格范围: $150.00 - $170.00
- 止损位（保护本金）: $140.00
- 止盈位（锁定收益）: $165.00
```

### 概率评估
```
📊 概率分析
| 可能性 | 概率 |
|-------|------|
| 📈 股价上升 | 70% |
| 📉 股价下降 | 20% |
| ➡️ 价格盘整 | 10% |
```

### 操作建议
```
💰 操作建议（不是财务建议）
1. 对于想买的人: 在 $145.50 附近买入，分批建仓
2. 对于已持有的人: 继续持有，可以考虑逢低加仓
3. 资金管理: 不要押上全部身家，风险承受能力有限的话只投资 1-5% 的资本
```

---

## ⚙️ 核心改进技术细节

### DecisionCard 类
```python
from decision_card import DecisionCard, Signal, Confidence

card = DecisionCard(
    ticker="NVDA",
    signal=Signal.BUY,
    confidence=Confidence.HIGH,
    target_price_low=150.00,
    target_price_high=170.00,
    entry_price=145.50,
    stop_loss_price=140.00,
    take_profit_price=165.00,
    upside_probability=70.0,
    downside_probability=20.0,
    sideways_probability=10.0,
    bullish_catalyst="强劲的Q3收益报告",
    bearish_catalyst="AI芯片需求下降风险",
    key_risks=["市场波动风险", "宏观经济下滑风险"],
)

# 输出
print(card.to_markdown())      # Markdown格式
print(card.to_simple_text())   # 简单文本
print(card.to_dict())          # JSON兼容字典
```

### Terminology 使用
```python
from terminology import get_simple_term, get_explanation, TERMINOLOGY_MAP

# 获取简单术语
simple = get_simple_term("RSI")  # "买卖热度"

# 获取解释
explanation = get_explanation("RSI")  
# "0-100的数值，表示股票被超买或超卖的程度..."

# 查看所有映射
for term, mapping in TERMINOLOGY_MAP.items():
    print(f"{term} → {mapping['simple']}")
```

### 生成简化报告
```python
from simple_report_generator import generate_simple_markdown_report

report = generate_simple_markdown_report(
    snapshot, indicators, news, score, strategy, decision_card
)
print(report)
```

---

## 📈 投资决策流程

```
输入: 股票代码 (e.g., NVDA)
    ↓
[数据层]
├── 获取市场数据 (价格、成交量)
├── 获取新闻和公告
└── 获取宏观数据
    ↓
[分析层]
├── 计算技术指标 (RSI, MACD, 布林带)
└── 生成图表
    ↓
[核心层]
├── 评分引擎
│   ├── 技术面评分 (30%)
│   ├── 基本面评分 (25%)
│   ├── 新闻面评分 (20%)
│   ├── 情绪面评分 (15%)
│   └── 宏观面评分 (10%)
│
└── 策略生成器
    ├── 生成 BUY/SELL/HOLD 信号
    ├── 计算进场/止损/止盈价格
    ├── 评估概率分布
    └── 识别关键催化剂
    ↓
[报告层]
├── 决策卡生成 (清晰的投资行动)
├── 简化报告生成 (通俗易懂)
└── 输出 (Markdown/JSON)
    ↓
输出: 投资分析报告和建议
```

---

## 🔄 迁移和兼容性

本次改进**完全向后兼容**：

- ✅ `investment_advisor.py` 仍然可用，且功能增强
- ✅ `full_analysis.py` 仍然可用
- ✅ 所有原有数据模型保留
- ✅ 现有脚本可继续使用（import 无需改动）

**逐步迁移计划**:
1. 新项目使用 `format=simple` 获取易读报告
2. 逐步将专业分析 migrate 到新 decision_card 类
3. 最终目标：统一所有报告通过 reports/ 目录生成

---

## 📚 下一步工作

计划在未来迭代中：

- [ ] 将所有文件正式迁移到 core/, data/, analysis/, reports/ 目录
- [ ] 创建统一的 reports/report_generator.py
- [ ] 添加多语言支持（中文/英文切换）
- [ ] 支持实时更新报告（watch mode）
- [ ] 生成 PDF 格式报告
- [ ] 添加更多图表和可视化
- [ ] 集成 web UI for 实时分析

---

## 💬 反馈和建议

如果你对报告的清晰度或格式有任何建议，欢迎提出：

- 是否术语足够通俗？
- 是否信号足够明确？
- 还需要什么额外的信息？
- 有没有遗漏的投资建议？

---

**版本**: v0.2 (2026-05-29)  
**最后更新**: 投资决策卡、简化报告、术语映射完成  
