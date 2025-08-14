import asyncio, json, os
from typing import List, Dict
import openai

openai.api_key = os.getenv("VERCEL_AI_TOKEN", "")

class OptimizedAIExtractor:
async def extract_events_chunked(self, html_chunks: List[str], city: str) -> List[Dict]:
events = []
for chunk in html_chunks:
part = await self.extract_single_chunk(chunk, city)
if part: events.extend(part)
return self.dedup(events)


async def extract_single_chunk(self, html: str, city: str) -> List[Dict]:
    prompt = f"""
Return ONLY a JSON array of events. Fields: title, category, date, time, venue, price, website.
City: {city}
HTML:
{html[:5000]}
"""
try:
resp = await asyncio.to_thread(openai.chat.completions.create,
model="gpt-4o-mini",
messages=[{"role":"user","content":prompt}],
temperature=0.2,
max_tokens=1200)
txt = resp.choices.message.content.strip()
data = json.loads(txt)
return data if isinstance(data, list) else []
except Exception:
return []


def dedup(self, items: List[Dict]) -> List[Dict]:
    seen, out = set(), []
    for e in items:
        key = (e.get("title","").lower(), e.get("venue","").lower(), e.get("date",""))
        if key not in seen and e.get("title"):
            seen.add(key); out.append(e)
    return out
