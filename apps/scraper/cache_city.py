import os, json, asyncio, argparse
from datetime import datetime
import redis
from dotenv import load_dotenv
from scraping_engine import ScrapingEngine
from ai_extractor import OptimizedAIExtractor

load_dotenv()

class CityCache:
def init(self):
self.redis = redis.from_url(os.getenv("UPSTASH_REDIS_URL"))
self.scraper = ScrapingEngine()
self.ai = OptimizedAIExtractor()


def load_city_config(self, city: str):
    with open("config/cities.json","r") as f:
        cfg = json.load(f)
    return cfg.get("cities",{}).get(city.lower())

async def cache_city(self, city: str):
    cfg = self.load_city_config(city)
    if not cfg: 
        print("No config for", city); return
    pages = await self.scraper.scrape_city_sources(cfg)
    events = await self.ai.extract_events_chunked(pages, city)
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"events:{city.lower()}:{today}"
    status = f"status:{city.lower()}:lastUpdated"
    ttl = 7200 if cfg.get("popular") else 21600
    self.redis.setex(key, ttl, json.dumps(events))
    self.redis.setex(status, ttl, datetime.now().isoformat())
    print(f"Cached {len(events)} events for {city}")
async def main():
ap = argparse.ArgumentParser()
ap.add_argument("--city", required=True)
args = ap.parse_args()
c = CityCache()
await c.cache_city(args.city)

if name == "main":
asyncio.run(main())
