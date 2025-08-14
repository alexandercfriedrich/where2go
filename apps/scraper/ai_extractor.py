import asyncio
import json
import os
from typing import List, Dict

# OpenAI v1 Client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore


class OptimizedAIExtractor:
    def __init__(self):
        # Nutzt OpenAI- oder Vercel-AI-Gateway-Key im gleichen Env-Var
        self.api_key = os.getenv("VERCEL_AI_TOKEN", "")
        self.client = OpenAI(api_key=self.api_key) if (OPENAI_AVAILABLE and self.api_key) else None

    async def extract_events_chunked(self, html_chunks: List[str], city: str) -> List[Dict]:
        """
        Verarbeite HTML in Chunks, extrahiere Events via LLM.
        Gibt am Ende eine de-duplizierte Liste zurück.
        """
        events: List[Dict] = []

        # Fallback ohne LLM: nichts crashen lassen
        if not self.client:
            return []

        for idx, chunk in enumerate(html_chunks):
            part = await self.extract_single_chunk(chunk, city, idx)
            if part:
                events.extend(part)

        return self.dedup(events)

    async def extract_single_chunk(self, html: str, city: str, chunk_id: int) -> List[Dict]:
        """
        Ein einzelnes HTML-Chunk mit dem Modell verarbeiten.
        Erwartet ein reines JSON-Array als Antwort.
        """
        prompt = f"""
Return ONLY a JSON array of events with objects using these fields:
"title", "category", "date", "time", "venue", "price", "website".
City: {city}
Rules:
- Output must be a pure JSON array (no comments, no explanation).
- If nothing is found, return [].

HTML (truncated):
{html[:5000]}
"""

        try:
            # OpenAI v1-SDK Aufruf in Thread ausführen, um async kompatibel zu bleiben
            resp = await asyncio.to_thread(
                self.client.chat.completions.create,  # type: ignore
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1200,
            )
            txt = resp.choices[0].message.content.strip()  # type: ignore

            # Versuche JSON zu parsen
            data = json.loads(txt)
            if isinstance(data, list):
                # Sanity-Cleaning der Felder
                cleaned: List[Dict] = []
                for e in data:
                    cleaned.append({
                        "title": (e.get("title") or "").strip(),
                        "category": (e.get("category") or "").strip(),
                        "date": (e.get("date") or "").strip(),
                        "time": (e.get("time") or "").strip(),
                        "venue": (e.get("venue") or "").strip(),
                        "price": (e.get("price") or "").strip(),
                        "website": (e.get("website") or "").strip(),
                    })
                return cleaned
            else:
                return []
        except json.JSONDecodeError:
            # Falls das Modell Text um das JSON herum geliefert hat, versuche simpel zu extrahieren
            try:
                start = txt.find("[")
                end = txt.rfind("]")
                if start != -1 and end != -1 and end > start:
                    snippet = txt[start : end + 1]
                    data = json.loads(snippet)
                    return data if isinstance(data, list) else []
            except Exception:
                return []
            return []
        except Exception as e:
            # Keine harten Fehler, damit der Job weiterläuft
            print(f"AI extraction error (chunk {chunk_id}): {repr(e)}")
            return []

    def dedup(self, items: List[Dict]) -> List[Dict]:
        """
        Entferne Duplikate (Titel + Venue + Datum
