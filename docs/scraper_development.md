# Developing a Scraper Plugin

## Architecture
GovTrack AI uses a decoupled plugin architecture. To add a new government organization, you ONLY need to create a single python file inside `scrapers/plugins/`.

## Lifecycle
Every scraper must inherit from `BaseScraper` and implement:
1. `fetch_recruitment_page()`: Returns raw HTML/JSON.
2. `extract_notifications(html)`: Returns a list of raw dictionaries.

The `BaseScraper.execute()` method automatically handles:
- Change Detection (via Hashes)
- Normalization (Standardized Job object)
- Downloading documents (duplicate aware)
- DB Insertion (Validation checked)

## Example
```python
from scrapers.base_scraper import BaseScraper

class ExampleScraper(BaseScraper):
    org_id = "exam_gov"
    org_name = "Example Gov"

    def fetch_recruitment_page(self):
        res = self.request_engine.get("http://example.gov/careers")
        return res.text

    def extract_notifications(self, html):
        # use utils.html_utils to parse
        return [{"title": "Job A"}]
```

## Best Practices
- Never use direct `requests`, always use `self.request_engine`.
- Never insert to the DB manually, let the `BaseScraper` manage lifecycle.
- Never write explicit deduplication, `ChangeDetector` handles this.
