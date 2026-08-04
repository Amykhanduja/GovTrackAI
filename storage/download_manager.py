import os
import hashlib
import logging
from urllib.parse import urlparse

logger = logging.getLogger('app.downloads')

class DownloadManager:
    def __init__(self, config):
        self.base_dir = config.get('download_dir', 'downloads/')
        self.downloaded_hashes = set()

    def download_for_job(self, org_id: str, job_obj: dict):
        docs = []
        for url in job_obj.get('document_links', []):
            if self._is_document(url):
                docs.append(self._download_file(org_id, url))
        return docs

    def _is_document(self, url):
        exts = ['.pdf', '.docx', '.zip', '.png', '.jpg', '.jpeg']
        return any(url.lower().endswith(ext) for ext in exts) or 'download' in url.lower()

    def _download_file(self, org_id, url):
        # Normalizes filename and avoids duplicates using URL hashing
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.downloaded_hashes:
            logger.debug(f"Skipping duplicate download: {url}")
            return None
        
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or f"doc_{url_hash}.pdf"
        
        # Create org-specific folder
        org_dir = os.path.join(self.base_dir, org_id)
        os.makedirs(org_dir, exist_ok=True)
        
        file_path = os.path.join(org_dir, filename)
        
        # In reality, perform actual request here
        logger.info(f"Simulating download of {url} to {file_path}")
        self.downloaded_hashes.add(url_hash)
        return file_path
