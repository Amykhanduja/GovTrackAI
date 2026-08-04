import platform
import psutil
import json
import os
from datetime import datetime
from core.data_manager import DataManager

class DiagnosticReporter:
    def __init__(self):
        self.dm = DataManager()
        
    def generate_crash_report(self, exception_trace: str):
        report = {
            "timestamp": datetime.now().isoformat(),
            "os": platform.platform(),
            "python_version": platform.python_version(),
            "memory_usage_mb": psutil.virtual_memory().used / (1024*1024),
            "traceback": exception_trace
        }
        
        report_path = os.path.join(self.dm.base_path, "logs", f"crash_report_{datetime.now().timestamp()}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
        return report_path
