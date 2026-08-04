import concurrent.futures
import logging
from typing import List, Callable

logger = logging.getLogger('app.async_worker')

class AsyncExecutionEngine:
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

    def execute_in_parallel(self, func: Callable, items: List, batch_size: int = 50):
        # Process items in batches to optimize memory usage
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            logger.debug(f"Executing batch {i//batch_size + 1}")
            futures = [self.executor.submit(func, item) for item in batch]
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Task failed: {e}")
        return results
