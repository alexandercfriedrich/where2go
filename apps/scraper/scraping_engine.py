import asyncio, aiohttp
from typing import List, Dict

SOURCES_LIMIT_PER_CITY = 10
TIMEOUT = aiohttp.ClientTimeout(total=20)

class ScrapingEngine:
async def fetch(self, session, url):
try:
async with session.get(url, timeout=TIMEOUT, headers={"User-Agent": "where2go-bot/1.0"}) as resp:
if resp.status == 200:
return await resp.text()
except Exception:
return ""
return ""

async def scrape_city_sources(self, city_config: Dict) -> List[str]:
    urls = city_config.get("sources", [])[:SOURCES_LIMIT_PER_CITY]
    if not urls:
        return []
    async with aiohttp.ClientSession() as session:
        tasks = [self.fetch(session, u) for u in urls]
        pages = await asyncio.gather(*tasks, return_exceptions=True)
        return [p for p in pages if isinstance(p, str) and p.strip()]
