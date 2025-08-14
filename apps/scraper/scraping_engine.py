import asyncio
import aiohttp
from typing import List, Dict

SOURCES_LIMIT_PER_CITY = 10
TIMEOUT = aiohttp.ClientTimeout(total=30)  # etwas großzügiger

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            "User-Agent": "where2go-bot/1.0 (+https://where2go.at)"
        }

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            async with session.get(url, timeout=TIMEOUT, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    # Nicht crashen, nur leeren String zurückgeben
                    return ""
        except Exception:
            return ""

    async def scrape_city_sources(self, city_config: Dict) -> List[str]:
        urls = (city_config.get("sources") or [])[:SOURCES_LIMIT_PER_CITY]
        if not urls:
            return []

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, u) for u in urls]
            pages = await asyncio.gather(*tasks, return_exceptions=True)

        out: List[str] = []
        for p in pages:
            if isinstance(p, str) and p.strip():
                out.append(p)
        return out
