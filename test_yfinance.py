
import sys
print("Python version:", sys.version)
print("\nTesting imports...")

try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
except Exception as e:
    print(f"✗ yfinance import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting yfinance with NVDA...")
try:
    stock = yf.Ticker("NVDA")
    print("✓ Ticker created")
    
    print("\n--- Fetching info ---")
    info = stock.info
    print("✓ Info fetched")
    print(f"  Current price: {info.get('currentPrice', 'N/A')}")
    print(f"  Market cap: {info.get('marketCap', 'N/A')}")
    
    print("\n--- Fetching history ---")
    hist = stock.history(period="1mo")
    print(f"✓ History fetched, {len(hist)} rows")
    
    print("\n--- Testing complete ---")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

