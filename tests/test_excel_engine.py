import unittest
import os
from excel.engine import ExcelEngine

class TestExcelEngine(unittest.TestCase):
    def setUp(self):
        self.config = {'output_dir': 'downloads/test_reports'}
        self.engine = ExcelEngine(self.config)

    def test_workbook_generation(self):
        self.engine.generate()
        self.assertTrue(os.path.exists(self.engine.file_path))
        # Ensure it has size
        self.assertTrue(os.path.getsize(self.engine.file_path) > 1000)

    def tearDown(self):
        if os.path.exists(self.engine.file_path):
            os.remove(self.engine.file_path)
