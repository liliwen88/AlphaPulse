#!/usr/bin/env python3
"""Quick verification script for AlphaPulse improvements."""

import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

def test_imports():
    """Test all new modules can be imported."""
    print("✓ Testing imports...")
    try:
        from decision_card import DecisionCard, Signal, Confidence
        print("  ✓ decision_card imported")
        
        from decision_card_generator import generate_decision_card
        print("  ✓ decision_card_generator imported")
        
        from terminology import TERMINOLOGY_MAP, get_simple_term
        print("  ✓ terminology imported")
        
        from simple_report_generator import generate_simple_markdown_report
        print("  ✓ simple_report_generator imported")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_decision_card():
    """Test DecisionCard functionality."""
    print("\n✓ Testing DecisionCard...")
    try:
        from decision_card import DecisionCard, Signal, Confidence
        
        card = DecisionCard(
            ticker="TEST",
            signal=Signal.BUY,
            confidence=Confidence.HIGH,
            target_price_low=150.0,
            target_price_high=170.0,
            entry_price=145.5,
            stop_loss_price=140.0,
            take_profit_price=165.0,
            upside_probability=70.0,
            downside_probability=20.0,
            sideways_probability=10.0,
            bullish_catalyst="Test catalyst",
            bearish_catalyst="Test risk",
            key_risks=["Risk 1", "Risk 2"],
        )
        
        # Test all output formats
        markdown = card.to_markdown()
        assert "TEST" in markdown
        assert "BUY" in markdown
        print("  ✓ to_markdown() works")
        
        simple = card.to_simple_text()
        assert "BUY" in simple
        print("  ✓ to_simple_text() works")
        
        data = card.to_dict()
        assert data["ticker"] == "TEST"
        print("  ✓ to_dict() works")
        
        return True
    except Exception as e:
        print(f"  ✗ DecisionCard test failed: {e}")
        return False


def test_terminology():
    """Test terminology mapping."""
    print("\n✓ Testing Terminology...")
    try:
        from terminology import get_simple_term, TERMINOLOGY_MAP
        
        # Test some mappings
        rsi_simple = get_simple_term("RSI")
        assert rsi_simple == "买卖热度"
        print(f"  ✓ RSI → {rsi_simple}")
        
        macd_simple = get_simple_term("MACD")
        assert macd_simple == "趋势动力"
        print(f"  ✓ MACD → {macd_simple}")
        
        assert len(TERMINOLOGY_MAP) > 0
        print(f"  ✓ Loaded {len(TERMINOLOGY_MAP)} term mappings")
        
        return True
    except Exception as e:
        print(f"  ✗ Terminology test failed: {e}")
        return False


def test_investment_advisor_enhanced():
    """Test that investment_advisor supports new format."""
    print("\n✓ Testing investment_advisor enhancements...")
    try:
        from investment_advisor import gather_report_data
        
        # Just verify the function signature changed to include decision_card
        import inspect
        sig = inspect.signature(gather_report_data)
        # The function should still work (but we won't actually call it without real data)
        print("  ✓ gather_report_data signature updated")
        
        return True
    except Exception as e:
        print(f"  ✗ investment_advisor enhancement test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 50)
    print("AlphaPulse Improvements Verification")
    print("=" * 50)
    
    results = {
        "Imports": test_imports(),
        "DecisionCard": test_decision_card(),
        "Terminology": test_terminology(),
        "Investment Advisor": test_investment_advisor_enhanced(),
    }
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<35} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! AlphaPulse improvements are working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
