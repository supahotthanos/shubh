"""
Authority Signals Tracker

Tracks domain authority metrics from Common Crawl WebGraph,
including Harmonic Centrality and PageRank.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
import httpx
from urllib.parse import urlparse


@dataclass
class AuthorityMetrics:
    domain: str
    harmonic_centrality_rank: Optional[int]
    harmonic_centrality_score: Optional[float]
    pagerank_score: Optional[float]
    pagerank_rank: Optional[int]
    domain_rating: Optional[float]  # Ahrefs
    domain_authority: Optional[float]  # Moz
    referring_domains: Optional[int]
    total_backlinks: Optional[int]
    has_wikipedia_citation: bool
    wikipedia_url: Optional[str]
    is_subdomain: bool
    root_domain: str
    authority_dilution_warning: bool
    dilution_explanation: Optional[str]
    measured_at: datetime


# Domains known to dilute authority (platform content)
AUTHORITY_DILUTION_DOMAINS = {
    "medium.com": "Content on Medium benefits Medium's authority, not yours",
    "linkedin.com": "LinkedIn articles don't build domain authority for external sites",
    "substack.com": "Substack newsletters build Substack's authority",
    "wordpress.com": "Free WordPress.com sites have shared authority",
    "blogger.com": "Blogger pages share authority with Google",
    "wix.com": "Wix sites share authority with platform",
    "squarespace.com": "Squarespace sites have partial authority dilution",
    "github.io": "GitHub Pages build GitHub's authority",
    "notion.so": "Notion pages build Notion's authority",
    "docs.google.com": "Google Docs build Google's authority",
}


class AuthorityTrackerService:
    """
    Track and analyze domain authority signals.

    Integrates with:
    - Common Crawl WebGraph data
    - Third-party SEO APIs (Ahrefs, Moz, etc.)
    - Wikipedia citation checking
    """

    def __init__(
        self,
        ahrefs_api_key: Optional[str] = None,
        moz_api_key: Optional[str] = None,
    ):
        self.ahrefs_key = ahrefs_api_key
        self.moz_key = moz_api_key

    async def analyze_domain(self, domain: str) -> AuthorityMetrics:
        """
        Comprehensive authority analysis for a domain.
        """
        # Normalize domain
        domain = self._normalize_domain(domain)
        root_domain = self._get_root_domain(domain)
        is_subdomain = domain != root_domain

        # Check for authority dilution
        dilution_warning, dilution_reason = self._check_authority_dilution(domain)

        # Gather metrics from various sources
        webgraph_metrics = await self._fetch_webgraph_metrics(domain)
        seo_metrics = await self._fetch_seo_metrics(domain)
        wikipedia_info = await self._check_wikipedia_citation(domain)

        return AuthorityMetrics(
            domain=domain,
            harmonic_centrality_rank=webgraph_metrics.get("hc_rank"),
            harmonic_centrality_score=webgraph_metrics.get("hc_score"),
            pagerank_score=webgraph_metrics.get("pagerank"),
            pagerank_rank=webgraph_metrics.get("pagerank_rank"),
            domain_rating=seo_metrics.get("domain_rating"),
            domain_authority=seo_metrics.get("domain_authority"),
            referring_domains=seo_metrics.get("referring_domains"),
            total_backlinks=seo_metrics.get("total_backlinks"),
            has_wikipedia_citation=wikipedia_info["has_citation"],
            wikipedia_url=wikipedia_info.get("url"),
            is_subdomain=is_subdomain,
            root_domain=root_domain,
            authority_dilution_warning=dilution_warning,
            dilution_explanation=dilution_reason,
            measured_at=datetime.utcnow(),
        )

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain to consistent format"""
        domain = domain.lower().strip()
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")
        domain = domain.split("/")[0]
        return domain

    def _get_root_domain(self, domain: str) -> str:
        """Extract root domain from potentially subdomain"""
        parts = domain.split(".")

        # Handle special cases like co.uk, com.au
        special_tlds = ["co.uk", "com.au", "co.nz", "org.uk"]
        for tld in special_tlds:
            if domain.endswith(tld):
                # Domain is like "example.co.uk"
                tld_parts = tld.split(".")
                if len(parts) > len(tld_parts):
                    return ".".join(parts[-(len(tld_parts) + 1):])
                return domain

        # Standard TLD - take last two parts
        if len(parts) > 2:
            return ".".join(parts[-2:])
        return domain

    def _check_authority_dilution(self, domain: str) -> tuple[bool, Optional[str]]:
        """Check if domain is on a platform that dilutes authority"""
        root = self._get_root_domain(domain)

        for platform, reason in AUTHORITY_DILUTION_DOMAINS.items():
            if root == platform or domain.endswith("." + platform):
                return True, reason

        return False, None

    async def _fetch_webgraph_metrics(self, domain: str) -> Dict:
        """WebGraph HC/PageRank. Uses provider (mock or composite-real)."""
        from app.providers import get_authority_provider

        data = await get_authority_provider().authority_for(domain)
        return {
            "hc_rank": data.hc_rank,
            "hc_score": data.hc_score,
            "pagerank": data.pagerank_score,
            "pagerank_rank": data.pagerank_rank,
        }

    async def _fetch_seo_metrics(self, domain: str) -> Dict:
        """Pull DR / DA / backlinks via the authority provider."""
        from app.providers import get_authority_provider

        data = await get_authority_provider().authority_for(domain)
        return {
            "domain_rating": data.domain_rating,
            "domain_authority": data.domain_authority,
            "referring_domains": data.referring_domains,
            "total_backlinks": data.total_backlinks,
        }

    async def _fetch_ahrefs_metrics(self, domain: str) -> Dict:
        return await self._fetch_seo_metrics(domain)

    async def _fetch_moz_metrics(self, domain: str) -> Dict:
        return await self._fetch_seo_metrics(domain)

    async def _check_wikipedia_citation(self, domain: str) -> Dict:
        from app.providers import get_wikipedia_provider

        has, url = await get_wikipedia_provider().has_citation(domain)
        return {"has_citation": has, "url": url}

    async def compare_competitors(
        self, client_domain: str, competitor_domains: List[str]
    ) -> Dict:
        """Compare authority metrics across competitors"""
        all_domains = [client_domain] + competitor_domains
        results = []

        for domain in all_domains:
            metrics = await self.analyze_domain(domain)
            results.append({
                "domain": domain,
                "is_client": domain == client_domain,
                "hc_rank": metrics.harmonic_centrality_rank,
                "pagerank": metrics.pagerank_score,
                "domain_rating": metrics.domain_rating,
                "referring_domains": metrics.referring_domains,
                "has_wikipedia": metrics.has_wikipedia_citation,
            })

        # Sort by authority (lower HC rank = higher authority)
        results.sort(
            key=lambda x: x.get("hc_rank") or float("inf")
        )

        # Add rankings
        for i, result in enumerate(results):
            result["position"] = i + 1

        # Find client position
        client_position = next(
            (r["position"] for r in results if r["is_client"]),
            len(results)
        )

        return {
            "rankings": results,
            "client_position": client_position,
            "total_competitors": len(competitor_domains),
            "analysis": self._generate_competitive_analysis(results, client_domain),
        }

    def _generate_competitive_analysis(
        self, rankings: List[Dict], client_domain: str
    ) -> List[str]:
        """Generate insights from competitive analysis"""
        insights = []

        client = next((r for r in rankings if r["is_client"]), None)
        if not client:
            return insights

        position = client["position"]
        total = len(rankings)

        if position == 1:
            insights.append(
                "Your domain has the highest authority among tracked competitors."
            )
        elif position <= total // 3:
            insights.append(
                f"Your domain ranks #{position} out of {total} - in the top tier."
            )
        elif position <= 2 * total // 3:
            insights.append(
                f"Your domain ranks #{position} out of {total} - middle of the pack."
            )
        else:
            insights.append(
                f"Your domain ranks #{position} out of {total} - authority building needed."
            )

        # Check for Wikipedia citations
        wiki_leaders = [r for r in rankings if r.get("has_wikipedia") and not r["is_client"]]
        if wiki_leaders and not client.get("has_wikipedia"):
            insights.append(
                f"{len(wiki_leaders)} competitor(s) have Wikipedia citations. "
                "Consider PR/notability strategies."
            )

        return insights

    def get_authority_improvement_recommendations(
        self, metrics: AuthorityMetrics
    ) -> List[Dict]:
        """Generate recommendations for improving authority"""
        recommendations = []

        if metrics.authority_dilution_warning:
            recommendations.append({
                "priority": "critical",
                "title": "Authority Dilution Detected",
                "description": metrics.dilution_explanation,
                "action": "Consider hosting content on your own domain to build direct authority.",
            })

        if not metrics.has_wikipedia_citation:
            recommendations.append({
                "priority": "high",
                "title": "No Wikipedia Citation",
                "description": "Wikipedia citations are strong trust signals for AI systems.",
                "action": "Build brand notability through press coverage and industry recognition.",
            })

        if metrics.referring_domains and metrics.referring_domains < 100:
            recommendations.append({
                "priority": "high",
                "title": "Limited Backlink Profile",
                "description": f"Only {metrics.referring_domains} referring domains detected.",
                "action": "Focus on quality content marketing and digital PR to earn backlinks.",
            })

        if metrics.is_subdomain:
            recommendations.append({
                "priority": "medium",
                "title": "Content on Subdomain",
                "description": "Subdomain content may not fully benefit from root domain authority.",
                "action": "Consider consolidating important content to the main domain.",
            })

        return recommendations
