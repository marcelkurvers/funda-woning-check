import httpx
from bs4 import BeautifulSoup
import re
import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_photo_extraction():
    url = "https://www.funda.nl/detail/koop/waalre/huis-hendrik-van-cuyklaan-10/43168164/"
    logger.info(f"--- TESTING EXTRACTION FOR: {url} ---")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,nl;q=0.8",
    }
    
    try:
        with httpx.Client(follow_redirects=True, headers=headers, timeout=30.0) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch page: {resp.status_code}")
                return
            
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")
            
            # --- METHOD 1: OG:IMAGE (The previous working method) ---
            logger.info("\n[Method 1] Checking meta og:image...")
            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                logger.info(f"✅ FOUND OG:IMAGE: {og_img.get('content')}")
            else:
                logger.info("❌ OG:IMAGE not found")

            # --- METHOD 2: NUXT_DATA (The new high-res gallery) ---
            logger.info("\n[Method 2] Checking __NUXT_DATA__...")
            script = soup.find("script", id="__NUXT_DATA__")
            if script:
                try:
                    ids = re.findall(r'(\d{3}/\d{3}/\d{3})', script.string)
                    unique_ids = list(dict.fromkeys(ids))
                    logger.info(f"✅ FOUND {len(unique_ids)} photo IDs in NUXT")
                    for mid in unique_ids[:3]:
                        logger.info(f"   -> https://cloud.funda.nl/valentina_media/{mid}.jpg?options=width=1440")
                except Exception as e:
                    logger.info(f"❌ Pattern Search Error: {e}")
            else:
                logger.info("❌ __NUXT_DATA__ block not found")

            # --- METHOD 3: DOM SCRAPE (Nuxt CDN) ---
            logger.info("\n[Method 3] Checking DOM img tags (Strict Filter)...")
            imgs = soup.find_all("img")
            dom_photos = []
            for img in imgs:
                src = img.get("src") or img.get("data-src")
                if not src: continue
                
                if "funda.nl" in src:
                    alt = (img.get("alt") or "").lower()
                    if "logo" in alt or "funda" in alt: continue
                    
                    if "cloud.funda.nl" in src:
                        high_res = re.sub(r'width=\d+', 'width=1440', src)
                    else:
                        high_res = re.sub(r'_[0-9]+x[0-9]+', '_1440x960', src)
                    dom_photos.append(high_res)
            
            unique_dom = list(dict.fromkeys(dom_photos))
            logger.info(f"✅ FOUND {len(unique_dom)} photos in DOM")
            for u in unique_dom[:3]:
                logger.info(f"   -> {u}")

    except Exception as e:
        logger.error(f"Test crashed: {e}")

if __name__ == "__main__":
    test_photo_extraction()
