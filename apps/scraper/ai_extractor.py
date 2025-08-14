import asyncio
import json
import os
from typing import List, Dict

# Fallback-kompatibel: funktionale API
OPENAI_AVAILABLE = False
try:
    import openai  # openai==1.30.1
    OPENAI_AVAILABLE = True
except Exception:
    openai = None  # type: ignore


class OptimizedAIExtractor:
    def __init__(self):
        # Nutzt OpenAI- oder Vercel-AI-Gateway-Key im gleichen Env-Var
        self.api_key = os.getenv("VERCEL_AI_TOKEN", "")
        if OPENAI_AVAILABLE and self.api_key:
            # Setze global den API-Key; keine Client-Init (vermeidet proxies-Problem)
            openai.api_key = self.api_key  # type: ignore

    async def extract_events_chunked(self, html_chunks: List[str], city: str) -> List[Dict]:
        """
        Verarbeitet mehrere HTML-Chunks und führt Event-Extraktion via LLM durch.
        Gibt eine de-duplizierte Liste zurück.
        """
        events: List[Dict] = []

        # Fallback ohne LLM-Key/Modul: gib leere Liste zurück (nicht crashen)
        if not (OPENAI_AVAILABLE and self.api_key):
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
        prompt = (
            "Return ONLY a JSON array of events with objects using these fields:\n"
            "\"title\", \"category\", \"date\", \"time\", \"venue\", \"price\", \"website\".\n"
            f"City: {city}\n"
            "Rules:\n"
            "- Output must be a pure JSON array (no comments, no explanation).\n"
            "- If nothing is found, return [].\n\n"
            "HTML (truncated):\n"
            f"{html[:5000]}\n"
        )

        try:
            # Aufruf der funktionalen API im Thread, um Async nicht zu blockieren
            resp = await asyncio.to_thread(
                openai.chat.completions.create,  # type: ignore
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1200,
            )
            txt = resp.choices[0].message.content.strip()  # type: ignore

            # JSON parsen
            data = json.loads(txt)
            if isinstance(data, list):
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
            return []
        except json.JSONDecodeError:
            # Fallback: JSON aus Text herausziehen
            try:
                start = txt.find("[")  # type: ignore
                end = txt.rfind("]")   # type: ignore
                if start != -1 and end != -1 and end > start:
                    snippet = txt[start : end + 1]  # type: ignore
                    data = json.loads(snippet)
                    return data if isinstance(data, list) else []
            except Exception:
                return []
            return []
        except Exception as e:
            print(f"AI extraction error (chunk {chunk_id}): {repr(e)}")
            return []

    def dedup(self, items: List[Dict]) -> List[Dict]:
        """
        Entfernt Duplikate basierend auf (title, venue, date).
        """
        seen = set()
        out: List[Dict] = []
        for e in items:
            key = (
                (e.get("title") or "").lower(),
                (e.get("venue") or "").lower(),
                (e.get("date") or "").strip(),
            )
            if key not in seen and (e.get("title") or "").strip():
                seen.add(key)
                out.append(e)
        return out
