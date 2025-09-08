from typing import Optional, Dict, Any, List
from datetime import datetime

class UrlRecord:
    def __init__(self, original_url: str, shortcode: str, expiry: Optional[datetime] = None):
        self.original_url = original_url
        self.shortcode = shortcode
        self.expiry = expiry
        self.creation_date = datetime.utcnow()
        self.click_count = 0
        self.click_logs: List[Dict[str, Any]] = []

    def log_click(self, referrer: Optional[str], geo: Optional[str] = None):
        self.click_count += 1
        self.click_logs.append({
            'timestamp': datetime.utcnow(),
            'referrer': referrer,
            'geo': geo
        })