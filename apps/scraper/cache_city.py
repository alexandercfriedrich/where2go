import os
import json
import asyncio
import argparse
from datetime import datetime

import redis
from dotenv import load_dotenv

from scraping_engine import ScrapingEngine
from ai_extractor import OptimizedAIExtractor

load_dotenv()

class CityCache:
    def __init__(self):
        url = os.getenv("UPSTASH_REDIS_URL")
        if not url:
            raise RuntimeError("UPSTASH_REDIS_URL missing")
        # Hinweis: Für Upstash REST-Token wird in diesem Skript kein separater Parameter benötigt,
        # da redis.from_url(url) mit rediss://… auskommt.
        self.redis = redis.from_url(url)
        self.scraper = ScrapingEngine()
        self.ai = OptimizedAIExtractor()

    def load_city_config(self, city: str) -> dict:
        with open("config/cities.json", "r") as f:
            cfg = json.load(f)
        return cfg.get("cities", {}).get(city.lower(), {})

    async def cache_city(self, city: str):
        cfg = self.load_city_config(city)
        if not cfg:
            print(f"No config for {city}")
            return

        print(f"Scraping sources for {city}...")
        pages = await self.scraper.scrape_city_sources(cfg)
        if not pages:
            print(f"No pages scraped for {city}")
            pages = []

        print(f"Extracting events with AI for {city}...")
        events = await self.ai.extract_events_chunked(pages, city)
        if events is None:
            events = []

        today = datetime.now().strftime("%Y-%m-%d")
        key = f"events:{city.lower()}:{today}"
        status = f"status:{city.lower()}:lastUpdated"
        ttl = 7200 if cfg.get("popular") else 21600  # 2h / 6h

        # Persistiere als JSON-String
        self.redis.setex(key, ttl, json.dumps(events, ensure_ascii=False))
        self.redis.setex(status, ttl, datetime.now().isoformat())

        print(f"Cached {len(events)} events for {city}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True, help="City name (e.g., wien)")
    args = parser.parse_args()

    cc = CityCache()
    await cc.cache_city(args.city)

if __name__ == "__main__":
    asyncio.run(main())
