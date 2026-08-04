import unittest
from core.cache import MemoryCache
from core.async_worker import AsyncExecutionEngine
from core.performance import BenchmarkProfiler

class TestPerformanceOptimizations(unittest.TestCase):
    def test_cache(self):
        cache = MemoryCache(ttl_seconds=10)
        cache.set("key1", "data")
        self.assertEqual(cache.get("key1"), "data")
        cache.invalidate("key1")
        self.assertIsNone(cache.get("key1"))

    def test_async_engine(self):
        engine = AsyncExecutionEngine(max_workers=2)
        def mock_task(x): return x * 2
        results = engine.execute_in_parallel(mock_task, [1, 2, 3, 4], batch_size=2)
        self.assertEqual(sum(results), 20)

    def test_profiler(self):
        profiler = BenchmarkProfiler()
        profiler.start()
        stats = profiler.stop()
        self.assertTrue('execution_time_seconds' in stats)
        self.assertTrue('memory_used_mb' in stats)
