"""Composite real authority provider (Ahrefs DR + Moz DA)."""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.providers.base import AuthorityData


class CompositeAuthorityProvider:
    async def authority_for(self, domain: str) -> AuthorityData:
        dr = rd = bl = None
        da = None
        async with httpx.AsyncClient(timeout=15.0) as client:
            if settings.AHREFS_API_KEY:
                try:
                    r = await client.get(
                        "https://apiv2.ahrefs.com",
                        params={
                            "target": domain,
                            "mode": "domain",
                            "token": settings.AHREFS_API_KEY,
                            "from": "domain_rating",
                            "output": "json",
                        },
                    )
                    if r.status_code == 200:
                        data = r.json()
                        dr = float(data.get("domain", {}).get("domain_rating", 0))
                        rd = int(data.get("domain", {}).get("refdomains", 0))
                        bl = int(data.get("domain", {}).get("backlinks", 0))
                except Exception:
                    pass
            if settings.MOZ_API_KEY:
                try:
                    r = await client.get(
                        "https://lsapi.seomoz.com/v2/url_metrics",
                        params={"targets[]": domain, "AccessID": settings.MOZ_API_KEY},
                    )
                    if r.status_code == 200:
                        data = r.json()
                        results = data.get("results") or []
                        if results:
                            da = float(results[0].get("domain_authority", 0))
                except Exception:
                    pass
        return AuthorityData(
            domain_rating=dr,
            domain_authority=da,
            referring_domains=rd,
            total_backlinks=bl,
        )
