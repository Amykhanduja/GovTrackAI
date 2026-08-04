import logging

logger = logging.getLogger('app.validation')

class RecordValidator:
    def validate_job(self, job_obj: dict) -> bool:
        if not job_obj.get('title'):
            logger.warning("Validation failed: Missing title")
            return False
        
        url = job_obj.get('notification_url')
        if url and not url.startswith('http'):
            logger.warning(f"Validation failed: Invalid URL {url}")
            return False
            
        return True
