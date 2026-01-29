"""
Content Freshness Analyzer

Based on ChatGPT's `use_freshness_scoring_profile: true` setting.
Analyzes content freshness and estimates impact on AI citations.
"""

import re
import hashlib
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import httpx
from bs4 import BeautifulSoup


class FreshnessGrade(str, Enum):
    A = "A"  # Fresh (< 3 months)
    B = "B"  # Good (3-6 months)
    C = "C"  # Aging (6-9 months)
    D = "D"  # Stale (9-12 months)
    F = "F"  # Outdated (> 12 months)


@dataclass
class FreshnessAnalysis:
    url: str
    last_modified: Optional[datetime]
    publish_date: Optional[datetime]
    update_date: Optional[datetime]
    content_hash: str
    days_since_update: int
    freshness_score: float  # 0-100
    freshness_grade: FreshnessGrade
    gpt_impact: str  # "minimal", "moderate", "significant", "severe"
    llama_impact: str
    gemini_impact: str
    estimated_position_loss: int
    refresh_priority: str  # "critical", "high", "medium", "low"
    recommendations: List[str]


# Model-specific freshness sensitivity
MODEL_FRESHNESS_CONFIG = {
    "gpt": {
        "optimal_months": 6,
        "warning_months": 9,
        "critical_months": 12,
        "position_loss_per_month": 8,  # After optimal period
    },
    "llama": {
        "optimal_months": 3,
        "warning_months": 6,
        "critical_months": 9,
        "position_loss_per_month": 12,
    },
    "gemini": {
        "optimal_months": 6,
        "warning_months": 9,
        "critical_months": 12,
        "position_loss_per_month": 7,
    },
    "qwen": {
        "optimal_months": 12,
        "warning_months": 18,
        "critical_months": 24,
        "position_loss_per_month": 5,
    },
}


class FreshnessAnalyzerService:
    """
    Analyze content freshness and estimate impact on AI citations.
    """

    def __init__(self):
        self.http_client = None

    async def analyze_url(self, url: str) -> FreshnessAnalysis:
        """
        Analyze freshness of a URL.

        Checks:
        1. HTTP Last-Modified header
        2. Published date in meta tags
        3. Updated date in meta tags
        4. Structured data dates
        5. In-content date patterns
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
            except Exception as e:
                return self._create_error_result(url, str(e))

        # Extract dates from response
        last_modified = self._parse_last_modified_header(response.headers)
        html = response.text
        content_hash = hashlib.sha256(html.encode()).hexdigest()[:16]

        soup = BeautifulSoup(html, "lxml")
        publish_date = self._extract_publish_date(soup)
        update_date = self._extract_update_date(soup)

        # Use the most recent date available
        reference_date = update_date or publish_date or last_modified
        if not reference_date:
            # Try to find date in content
            reference_date = self._extract_date_from_content(html)

        # Calculate metrics
        days_since = self._calculate_days_since(reference_date)
        freshness_score = self._calculate_freshness_score(days_since)
        freshness_grade = self._determine_grade(freshness_score)

        # Model-specific impact
        gpt_impact = self._calculate_model_impact(days_since, "gpt")
        llama_impact = self._calculate_model_impact(days_since, "llama")
        gemini_impact = self._calculate_model_impact(days_since, "gemini")

        position_loss = self._estimate_position_loss(days_since)
        refresh_priority = self._determine_priority(freshness_score, position_loss)
        recommendations = self._generate_recommendations(
            days_since, freshness_grade, publish_date, update_date
        )

        return FreshnessAnalysis(
            url=url,
            last_modified=last_modified,
            publish_date=publish_date,
            update_date=update_date,
            content_hash=content_hash,
            days_since_update=days_since,
            freshness_score=freshness_score,
            freshness_grade=freshness_grade,
            gpt_impact=gpt_impact,
            llama_impact=llama_impact,
            gemini_impact=gemini_impact,
            estimated_position_loss=position_loss,
            refresh_priority=refresh_priority,
            recommendations=recommendations,
        )

    def _parse_last_modified_header(
        self, headers: httpx.Headers
    ) -> Optional[datetime]:
        """Parse Last-Modified header"""
        last_mod = headers.get("Last-Modified")
        if not last_mod:
            return None

        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(last_mod)
        except Exception:
            return None

    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publish date from meta tags and structured data"""
        # Common meta tag patterns
        date_selectors = [
            ('meta[property="article:published_time"]', "content"),
            ('meta[name="publication_date"]', "content"),
            ('meta[name="date"]', "content"),
            ('meta[itemprop="datePublished"]', "content"),
            ('time[itemprop="datePublished"]', "datetime"),
            ('time[datetime]', "datetime"),
        ]

        for selector, attr in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get(attr)
                if date_str:
                    parsed = self._parse_date_string(date_str)
                    if parsed:
                        return parsed

        # Check JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    date_str = data.get("datePublished")
                    if date_str:
                        return self._parse_date_string(date_str)
            except Exception:
                continue

        return None

    def _extract_update_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract update/modified date from meta tags and structured data"""
        date_selectors = [
            ('meta[property="article:modified_time"]', "content"),
            ('meta[name="last-modified"]', "content"),
            ('meta[itemprop="dateModified"]', "content"),
            ('time[itemprop="dateModified"]', "datetime"),
        ]

        for selector, attr in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get(attr)
                if date_str:
                    parsed = self._parse_date_string(date_str)
                    if parsed:
                        return parsed

        # Check JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    date_str = data.get("dateModified")
                    if date_str:
                        return self._parse_date_string(date_str)
            except Exception:
                continue

        return None

    def _extract_date_from_content(self, html: str) -> Optional[datetime]:
        """Try to find date patterns in content"""
        # Common date patterns
        patterns = [
            r"(\d{4}-\d{2}-\d{2})",  # ISO format
            r"(\w+ \d{1,2}, \d{4})",  # Month DD, YYYY
            r"(\d{1,2}/\d{1,2}/\d{4})",  # MM/DD/YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                parsed = self._parse_date_string(match.group(1))
                if parsed:
                    return parsed

        return None

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats"""
        from dateutil import parser
        try:
            return parser.parse(date_str)
        except Exception:
            return None

    def _calculate_days_since(self, date: Optional[datetime]) -> int:
        """Calculate days since the given date"""
        if not date:
            return 365  # Assume 1 year if unknown

        now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
        delta = now - date
        return max(0, delta.days)

    def _calculate_freshness_score(self, days_since: int) -> float:
        """
        Calculate freshness score (0-100).

        100 = Just updated
        0 = Very stale (>2 years)
        """
        if days_since <= 30:
            return 100.0
        elif days_since <= 90:
            return 90.0 - ((days_since - 30) / 60) * 10
        elif days_since <= 180:
            return 80.0 - ((days_since - 90) / 90) * 20
        elif days_since <= 270:
            return 60.0 - ((days_since - 180) / 90) * 20
        elif days_since <= 365:
            return 40.0 - ((days_since - 270) / 95) * 20
        elif days_since <= 730:
            return 20.0 - ((days_since - 365) / 365) * 15
        else:
            return max(0, 5.0 - ((days_since - 730) / 365) * 5)

    def _determine_grade(self, score: float) -> FreshnessGrade:
        """Convert score to letter grade"""
        if score >= 80:
            return FreshnessGrade.A
        elif score >= 60:
            return FreshnessGrade.B
        elif score >= 40:
            return FreshnessGrade.C
        elif score >= 20:
            return FreshnessGrade.D
        else:
            return FreshnessGrade.F

    def _calculate_model_impact(self, days_since: int, model: str) -> str:
        """Calculate impact on specific model family"""
        config = MODEL_FRESHNESS_CONFIG.get(model, MODEL_FRESHNESS_CONFIG["gpt"])
        months = days_since / 30

        if months <= config["optimal_months"]:
            return "minimal"
        elif months <= config["warning_months"]:
            return "moderate"
        elif months <= config["critical_months"]:
            return "significant"
        else:
            return "severe"

    def _estimate_position_loss(self, days_since: int) -> int:
        """
        Estimate position loss due to staleness.

        Based on research showing 61-95 positions lost for very stale content.
        """
        months = days_since / 30
        config = MODEL_FRESHNESS_CONFIG["gpt"]

        if months <= config["optimal_months"]:
            return 0

        extra_months = months - config["optimal_months"]
        loss = int(extra_months * config["position_loss_per_month"])
        return min(loss, 95)  # Cap at 95

    def _determine_priority(self, score: float, position_loss: int) -> str:
        """Determine refresh priority"""
        if position_loss >= 50 or score < 20:
            return "critical"
        elif position_loss >= 30 or score < 40:
            return "high"
        elif position_loss >= 15 or score < 60:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        days_since: int,
        grade: FreshnessGrade,
        publish_date: Optional[datetime],
        update_date: Optional[datetime],
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if grade == FreshnessGrade.F:
            recommendations.append(
                "CRITICAL: Content is severely outdated. Immediate refresh required."
            )
            recommendations.append(
                "Update all statistics, examples, and references to current year."
            )
            recommendations.append(
                "Review for accuracy - outdated content may contain incorrect information."
            )
        elif grade == FreshnessGrade.D:
            recommendations.append(
                "Content is stale. Schedule refresh within 30 days to avoid citation loss."
            )
            recommendations.append(
                "Update the 'last modified' date after making substantive changes."
            )
        elif grade == FreshnessGrade.C:
            recommendations.append(
                "Content is aging. Plan refresh within 60 days."
            )
            recommendations.append(
                "Consider adding new sections or updated information."
            )
        elif grade == FreshnessGrade.B:
            recommendations.append(
                "Content freshness is good. Monitor for opportunities to update."
            )

        if not update_date:
            recommendations.append(
                "Add dateModified structured data to signal freshness to AI systems."
            )

        if days_since > 180:
            recommendations.append(
                "For LLaMA-based models, refresh every 3-6 months for optimal citation."
            )

        return recommendations

    def _create_error_result(self, url: str, error: str) -> FreshnessAnalysis:
        """Create result for failed analysis"""
        return FreshnessAnalysis(
            url=url,
            last_modified=None,
            publish_date=None,
            update_date=None,
            content_hash="",
            days_since_update=999,
            freshness_score=0.0,
            freshness_grade=FreshnessGrade.F,
            gpt_impact="unknown",
            llama_impact="unknown",
            gemini_impact="unknown",
            estimated_position_loss=0,
            refresh_priority="unknown",
            recommendations=[f"Error analyzing URL: {error}"],
        )

    def get_model_freshness_targets(self) -> List[Dict]:
        """Get recommended update frequencies by model family"""
        return [
            {
                "model_family": "GPT-based",
                "recommended_update_months": 6,
                "max_before_impact": 12,
                "notes": "ChatGPT uses freshness scoring profile",
            },
            {
                "model_family": "LLaMA-based",
                "recommended_update_months": 3,
                "max_before_impact": 6,
                "notes": "More sensitive to freshness",
            },
            {
                "model_family": "Gemini",
                "recommended_update_months": 6,
                "max_before_impact": 12,
                "notes": "Similar to GPT freshness handling",
            },
            {
                "model_family": "Qwen-based",
                "recommended_update_months": 12,
                "max_before_impact": 24,
                "notes": "Less sensitive to freshness",
            },
        ]
