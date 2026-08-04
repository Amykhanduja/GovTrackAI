class GovTrackError(Exception):
    """Base exception for all GovTrack errors."""
    pass

class SecurityError(GovTrackError):
    """Raised when a security violation (e.g. path traversal) occurs."""
    pass

class ConfigurationError(GovTrackError):
    """Raised when configuration validation fails."""
    pass

class DatabaseError(GovTrackError):
    """Raised when a database integrity or connection error occurs."""
    pass

class ScraperError(GovTrackError):
    """Raised when a scraper fails to download or parse data."""
    pass
