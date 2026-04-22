"""Deterministic mock GSC provider."""
from __future__ import annotations

import hashlib
import random
from typing import List

from app.providers.base import GSCProvider, GSCRow

_SEED_QUERIES = [
    "best crm software", "crm software comparison", "affordable crm tools",
    "semrush vs ahrefs", "ahrefs alternatives", "seo tools for agencies",
    "project management software", "asana vs monday", "best task manager 2025",
    "email marketing platform", "mailchimp alternatives", "transactional email service",
    "how to improve seo", "what is seo", "seo checklist 2025",
    "content marketing tools", "ai writing assistants", "chatgpt for business",
    "customer support software", "help desk tools", "live chat platforms",
    "analytics dashboard", "business intelligence tools", "data visualization",
    "accounting software small business", "invoice software", "bookkeeping app",
    "hr software", "payroll service", "applicant tracking system",
    "marketing automation", "lead generation tools", "sales enablement",
    "design software for teams", "figma alternatives", "collaborative design",
    "video conferencing", "zoom alternatives", "virtual meeting tools",
    "password manager", "security software", "identity management",
    "cloud storage", "file sharing platform", "document management",
    "no-code app builder", "low-code platform", "internal tools builder",
    "landing page builder", "form builder", "survey tools",
    "podcast hosting", "webinar software", "event management platform",
]


class MockGSCProvider:
    async def fetch_queries(
        self,
        property_url: str,
        days_back: int = 90,
        row_limit: int = 500,
    ) -> List[GSCRow]:
        seed = int(hashlib.sha256(property_url.encode()).hexdigest()[:16], 16)
        rng = random.Random(seed)
        count = min(row_limit, len(_SEED_QUERIES) * 3)
        rows: List[GSCRow] = []
        for i in range(count):
            base = _SEED_QUERIES[i % len(_SEED_QUERIES)]
            # create realistic variants
            suffix = rng.choice(["", " 2025", " for startups", " free", " reviews"])
            query = (base + suffix).strip()
            impressions = rng.randint(120, 25000)
            ctr = round(rng.uniform(0.01, 0.12), 4)
            clicks = int(impressions * ctr)
            position = round(rng.uniform(1.2, 48.0), 2)
            rows.append(
                GSCRow(
                    query=query,
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=position,
                )
            )
        return rows
