import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger('app.requests')

class RequestEngine:
    def __init__(self, config):
        self.session = requests.Session()
        self.timeout = config.get('timeout', 15)
        
        # Configure retries and backoff
        retries = Retry(
            total=config.get('max_retries', 3),
            backoff_factor=config.get('backoff_factor', 1),
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Default user agent placeholder
        self.session.headers.update({'User-Agent': 'GovTrackAI-Bot/1.0'})

    def get(self, url, headers=None, cookies=None, **kwargs):
        logger.debug(f"GET {url}")
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)
        return self.session.get(url, timeout=self.timeout, **kwargs)

    def post(self, url, data=None, json=None, headers=None, **kwargs):
        logger.debug(f"POST {url}")
        if headers:
            self.session.headers.update(headers)
        return self.session.post(url, data=data, json=json, timeout=self.timeout, **kwargs)
