import os
from exceptions.errors import SecurityError, ConfigurationError

class SecurityValidator:
    @staticmethod
    def validate_safe_path(base_dir: str, target_path: str) -> str:
        """Prevents Path Traversal attacks during document downloads/uploads."""
        abs_base = os.path.abspath(base_dir)
        abs_target = os.path.abspath(os.path.join(base_dir, target_path))
        
        if not abs_target.startswith(abs_base):
            raise SecurityError(f"Path Traversal Attack Detected: {target_path}")
        return abs_target

    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """
        Validates strings before allowing them near Raw SQL execution.
        Note: The project standard dictates using Parameterized Queries (?), 
        this acts as a secondary defense layer for dynamic sorting.
        """
        banned = [';', '--', 'DROP', 'INSERT', 'DELETE']
        upper_val = value.upper()
        if any(b in upper_val for b in banned):
            raise SecurityError("SQL Injection signature detected in input.")
        return value
        
    @staticmethod
    def validate_config(config: dict):
        """Validates critical configurations at startup."""
        if 'db_path' not in config:
            raise ConfigurationError("Database path missing from configuration.")
