class GovTrackError(Exception):
    pass
class ConfigurationError(GovTrackError):
    pass
class DatabaseError(GovTrackError):
    pass
class ScraperError(GovTrackError):
    pass
class ParserError(GovTrackError):
    pass
class DownloadError(GovTrackError):
    pass
class NotificationError(GovTrackError):
    pass
class AIError(GovTrackError):
    pass
class ExcelError(GovTrackError):
    pass
