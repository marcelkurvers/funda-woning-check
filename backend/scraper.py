import requests
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
]

class Scraper:
    def __init__(self):
        self.session = requests.Session()

    def get_headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch_page(self, url: str) -> str:
        """
        Fetches the page content.
        Returns HTML string if successful.
        Raises Exception if blocked (403/Captcha) or other error.
        """
        try:
            time.sleep(random.uniform(0.5, 1.5)) # Slight delay to be polite
            resp = self.session.get(url, headers=self.get_headers(), timeout=10)
            
            if resp.status_code == 403 or "captcha" in resp.url.lower():
                raise Exception("Blocked by Funda (403/Captcha). Use manual paste.")
            
            resp.raise_for_status()
            resp.encoding = "utf-8" # Ensure correct decoding
            return resp.text
            
        except requests.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
