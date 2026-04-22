"""Real Wikipedia citation checker."""
from __future__ import annotations

from typing import Optional

import httpx


class RealWikipediaProvider:
    async def has_citation(self, domain: str) -> tuple[bool, Optional[str]]:
        """Return True if any English Wikipedia page externally links to the domain."""
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "exturlusage",
            "euquery": domain,
            "eulimit": "1",
            "format": "json",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return False, None
        pages = data.get("query", {}).get("exturlusage", [])
        if pages:
            title = pages[0].get("title", "")
            return True, f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        return False, None
