"""
AlphaPulse - yfinance 缓存修复模块
在所有导入 yfinance 的脚本最前面先导入此模块
"""
import os
import sys

# Disable yfinance cache completely
os.environ["YFINANCE_CACHE_ENABLED"] = "False"
os.environ["YFINANCE_CACHE_DIR"] = ""
os.environ["YFINANCE_NO_CACHE"] = "1"

# Try to monkey-patch yfinance's cache system before importing yfinance
try:
    import importlib.util
    
    # First, patch the cache module if it exists
    yfinance_cache_spec = importlib.util.find_spec("yfinance.cache")
    if yfinance_cache_spec:
        # Create dummy cache module
        import types
        dummy_cache = types.ModuleType("yfinance.cache")
        
        # Create dummy Cache class
        class DummyCache:
            def __init__(self, *args, **kwargs):
            pass
        def initialise(self, *args, **kwargs):
            pass
        def lookup(self, *args, **kwargs):
            return None
        def store(self, *args, **kwargs):
            pass
        
        dummy_cache.Cache = DummyCache
        dummy_cache.TickerCache = DummyCache
        
        # Inject into sys.modules
        sys.modules["yfinance.cache"] = dummy_cache
        
except Exception:
    pass

# Now try to patch peewee (used by yfinance cache)
try:
    import importlib.util
    peewee_spec = importlib.util.find_spec("peewee")
    if peewee_spec:
        import types
        dummy_peewee = types.ModuleType("peewee")
        
        class DummyModel:
            def __init__(self, *args, **kwargs):
            pass
            
        class DummyDatabase:
            def __init__(self, *args, **kwargs):
                pass
            def connect(self, *args, **kwargs):
                return True
            def close(self, *args, **kwargs):
                pass
            def execute_sql(self, *args, **kwargs):
                return None
        
        dummy_peewee.Model = DummyModel
        dummy_peewee.SqliteDatabase = DummyDatabase
        dummy_peewee.OperationalError = Exception
        
        sys.modules["peewee"] = dummy_peewee
        
except Exception:
    pass

# Now import yfinance safely now
