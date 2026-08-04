import time
import logging
import psutil
import os

logger = logging.getLogger('app.performance')

class BenchmarkProfiler:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time.time()

    def stop(self) -> dict:
        self.end_time = time.time()
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        return {
            'execution_time_seconds': round(self.end_time - self.start_time, 4),
            'memory_used_mb': round(mem_info.rss / (1024 * 1024), 2)
        }
        
    def generate_report(self, module_name: str, stats: dict):
        logger.info(f"[PERF] {module_name} executed in {stats['execution_time_seconds']}s using {stats['memory_used_mb']}MB RAM")
