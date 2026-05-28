"""
AlphaPulse - 缓存修复模块
在导入 yfinance 之前先导入此模块
"""
import os
import sys

# 第一步：设置环境变量禁用缓存
os.environ["YFINANCE_CACHE_ENABLED"] = "False"
os.environ["YFINANCE_CACHE_DIR"] = ""
os.environ["YFINANCE_NO_CACHE"] = "1"
os.environ["YFINANCE_DISABLE_CACHE"] = "1"

# 第二步：在导入 yfinance 之前尝试 monkey-patch
try:
    # 创建假的 cache 模块
    import types
    fake_cache_module = types.ModuleType("yfinance.cache")
    
    class FakeCache:
        def __init__(self, *args, **kwargs):
            pass
        def initialise(self, *args, **kwargs):
            pass
        def lookup(self, *args, **kwargs):
            return None
        def store(self, *args, **kwargs):
            pass
    
    fake_cache_module.Cache = FakeCache
    fake_cache_module.TickerCache = FakeCache
    
    # 注册到 sys.modules
    sys.modules["yfinance.cache"] = fake_cache_module
    
    # 也可以尝试处理 peewee
    fake_peewee_module = types.ModuleType("peewee")
    
    class FakeSqliteDatabase:
        def __init__(self, *args, **kwargs):
            pass
        def connect(self, *args, **kwargs):
            return True
        def close(self, *args, **kwargs):
            pass
        def execute_sql(self, *args, **kwargs):
            return None
    
    fake_peewee_module.SqliteDatabase = FakeSqliteDatabase
    fake_peewee_module.OperationalError = Exception
    
    sys.modules["peewee"] = fake_peewee_module
    
except Exception:
    pass
