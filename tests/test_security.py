import unittest
from security.validator import SecurityValidator
from exceptions.errors import SecurityError

class TestSecurity(unittest.TestCase):
    def test_path_traversal_prevention(self):
        base = "/var/govtrack/data"
        # Should succeed
        safe = SecurityValidator.validate_safe_path(base, "resumes/my_resume.pdf")
        self.assertTrue(safe.startswith(base))
        
        # Should raise SecurityError
        with self.assertRaises(SecurityError):
            SecurityValidator.validate_safe_path(base, "../../../etc/passwd")

    def test_sql_injection_prevention(self):
        with self.assertRaises(SecurityError):
            SecurityValidator.sanitize_sql_input("id; DROP TABLE jobs;")
