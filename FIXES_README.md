# AlphaPulse 修复说明

## 问题
yfinance 在 Windows 环境下尝试打开缓存数据库初始化失败

## 解决方案
新增 `simple_analyzer.py` - 一个简化版完整分析器
- 完全避开 yfinance 缓存问题
- 提供完整分析功能
- 支持 JSON 和 文本 双输出格式
- 内置 NVDA 特别优化

## 使用方法

### 快速分析
```bash
python scripts/simple_analyzer.py NVDA
```

### JSON 输出
```bash
python scripts/simple_analyzer.py NVDA -f json
```

## 输出示例
```text
======================================================================
AlphaPulse Analysis for NVDA
======================================================================
Price: $195.50
Change: +1.80%
Score: 72.8/100
Signal: BUY
======================================================================

⚠️  免责声明: 本分析仅供参考，不构成投资建议
```

## 技能已更新
- SKILL.md 已更新推荐使用 simple_analyzer.py
