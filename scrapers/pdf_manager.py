import os
import json
import logging
import requests
from datetime import datetime
import hashlib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger('app.pdf_manager')

PDF_DIR = "/mnt/c/Users/khand/GovTrackAI/data/pdfs"
REGISTRY_FILE = os.path.join(PDF_DIR, "registry.json")

class PDFStorageManager:
    def __init__(self):
        os.makedirs(PDF_DIR, exist_ok=True)
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {}

    def _save_registry(self):
        with open(REGISTRY_FILE, "w") as f:
            json.dump(self.registry, f, indent=4)

    def download_if_needed(self, url: str, org_name: str, ad_number: str = None) -> str:
        """
        Downloads a PDF if it hasn't been downloaded yet or has changed.
        Returns the absolute local path to the PDF.
        Returns None if not a PDF or download fails.
        """
        if not url.startswith('http'):
            return None
            
        # Avoid duplicate downloads
        if url in self.registry:
            local_path = self.registry[url].get('local_path')
            if local_path and os.path.exists(local_path):
                return local_path

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            with requests.get(url, headers=headers, stream=True, timeout=20, verify=False) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()
                
                if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
                    return None
                    
                pdf_bytes = response.content
                file_hash = hashlib.md5(pdf_bytes).hexdigest()
                
                ad_str = (ad_number.replace("/", "-").replace("\\", "-").replace(" ", "_") 
                          if ad_number else f"HASH_{file_hash[:8]}")
                date_str = datetime.now().strftime("%Y%m%d")
                
                filename = f"{org_name}_{ad_str}_{date_str}.pdf"
                local_path = os.path.join(PDF_DIR, filename)
                
                with open(local_path, "wb") as f:
                    f.write(pdf_bytes)
                    
                self.registry[url] = {
                    "url": url,
                    "org_name": org_name,
                    "local_path": local_path,
                    "hash": file_hash,
                    "download_date": datetime.now().isoformat()
                }
                self._save_registry()
                return local_path
                
        except Exception as e:
            logger.error(f"Failed to download PDF {url}: {e}")
            return None
