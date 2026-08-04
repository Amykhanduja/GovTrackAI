import os
import logging

logger = logging.getLogger('app.career.documents')

class DocumentRepository:
    def __init__(self, storage_dir: str = 'data/documents'):
        self.storage_dir = storage_dir
        self.categories = ['resumes', 'identity', 'certificates', 'receipts', 'offer_letters']
        for cat in self.categories:
            os.makedirs(os.path.join(self.storage_dir, cat), exist_ok=True)

    def upload_document(self, category: str, file_path: str, metadata: dict = None) -> bool:
        if category not in self.categories:
            logger.error(f"Invalid category {category}")
            return False
        # Mock file copy logic
        logger.info(f"Uploaded {file_path} to {category}")
        return True
