"""
Google Search Console Importer

Transforms GSC ranking queries into AI visibility prompts.
Implements the GSC-to-AI Prompt Intelligence pipeline.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re


@dataclass
class GSCQuery:
    query: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class ConvertedPrompt:
    original_query: str
    conversational_prompt: str
    intent_type: str
    is_branded: bool
    gsc_metrics: GSCQuery
    cluster_id: Optional[int]
    conversion_confidence: float


@dataclass
class PromptCluster:
    id: int
    name: str
    prompts: List[ConvertedPrompt]
    total_impressions: int
    total_clicks: int
    avg_position: float


class GSCImporterService:
    """
    Import and transform Google Search Console data into AI prompts.

    Pipeline:
    1. Fetch GSC data via API
    2. Filter by minimum thresholds
    3. Convert fragmented keywords to conversational prompts
    4. Cluster semantically similar prompts
    5. Prioritize by traffic potential
    """

    # Common question prefixes to add for conversational conversion
    QUESTION_PREFIXES = [
        "What is the best",
        "How do I",
        "What are the top",
        "Which",
        "Can you recommend",
        "How to",
        "What's the difference between",
        "Is it worth",
        "Should I",
        "Where can I find",
    ]

    # Intent patterns
    INTENT_PATTERNS = {
        "informational": [
            r"^what\s", r"^how\s", r"^why\s", r"^when\s",
            r"^who\s", r"^where\s", r"guide", r"tutorial",
            r"explained", r"definition",
        ],
        "transactional": [
            r"buy", r"price", r"cost", r"cheap", r"discount",
            r"deal", r"coupon", r"purchase", r"order",
        ],
        "commercial": [
            r"best", r"top", r"review", r"vs", r"versus",
            r"comparison", r"alternative", r"compared",
        ],
        "navigational": [
            r"login", r"sign in", r"website", r"official",
            r"contact", r"support", r"download",
        ],
    }

    def __init__(self, gsc_credentials_path: Optional[str] = None):
        self.credentials_path = gsc_credentials_path
        self._service = None

    async def fetch_queries(
        self,
        property_url: str,
        days_back: int = 90,
        min_impressions: int = 1000,
        min_clicks: int = 10,
        max_position: float = 50.0,
    ) -> List[GSCQuery]:
        """
        Fetch queries from Google Search Console API.

        Args:
            property_url: GSC property URL (e.g., "https://example.com")
            days_back: Number of days of data to fetch
            min_impressions: Minimum impressions threshold
            min_clicks: Minimum clicks threshold
            max_position: Maximum average position

        Returns:
            List of GSCQuery objects
        """
        # In production, this would use the Google Search Console API
        # via google-api-python-client
        #
        # Example API call:
        # service.searchanalytics().query(
        #     siteUrl=property_url,
        #     body={
        #         "startDate": start_date,
        #         "endDate": end_date,
        #         "dimensions": ["query"],
        #         "rowLimit": 5000,
        #     }
        # ).execute()

        raise NotImplementedError("GSC API integration required")

    def convert_to_prompts(
        self,
        queries: List[GSCQuery],
        brand_names: List[str],
    ) -> List[ConvertedPrompt]:
        """
        Convert GSC queries to conversational AI prompts.

        Transforms fragmented keyword queries like:
        - "best seo tools 2024" -> "What are the best SEO tools in 2024?"
        - "semrush vs ahrefs" -> "What's the difference between SEMrush and Ahrefs?"
        """
        converted = []

        for query in queries:
            prompt, confidence = self._convert_query_to_prompt(query.query)
            intent = self._detect_intent(query.query)
            is_branded = self._check_branded(query.query, brand_names)

            converted.append(ConvertedPrompt(
                original_query=query.query,
                conversational_prompt=prompt,
                intent_type=intent,
                is_branded=is_branded,
                gsc_metrics=query,
                cluster_id=None,
                conversion_confidence=confidence,
            ))

        return converted

    def _convert_query_to_prompt(self, query: str) -> Tuple[str, float]:
        """
        Convert a search query to a conversational prompt.

        Returns:
            Tuple of (converted_prompt, confidence_score)
        """
        query = query.strip().lower()

        # Already a question - high confidence
        if query.startswith(("what", "how", "why", "when", "who", "where", "which", "can", "should", "is")):
            # Capitalize and add question mark if missing
            prompt = query.capitalize()
            if not prompt.endswith("?"):
                prompt += "?"
            return prompt, 0.95

        # "vs" or "versus" comparison
        if " vs " in query or " versus " in query:
            parts = re.split(r"\s+(?:vs|versus)\s+", query)
            if len(parts) == 2:
                return f"What's the difference between {parts[0]} and {parts[1]}?", 0.9

        # "best X" pattern
        if query.startswith("best "):
            topic = query[5:]
            return f"What are the best {topic}?", 0.9

        # "top X" pattern
        if query.startswith("top "):
            topic = query[4:]
            return f"What are the top {topic}?", 0.9

        # "X review" or "X reviews"
        if " review" in query:
            topic = query.replace(" reviews", "").replace(" review", "")
            return f"What are the reviews of {topic}?", 0.85

        # "how to X" without question format
        if "how to " in query:
            return query.capitalize() + "?", 0.9

        # "X alternative" or "X alternatives"
        if " alternative" in query:
            topic = query.replace(" alternatives", "").replace(" alternative", "")
            return f"What are some alternatives to {topic}?", 0.85

        # "X pricing" or "X cost"
        if " pricing" in query or " cost" in query or " price" in query:
            topic = re.sub(r"\s+(pricing|cost|price)s?", "", query)
            return f"How much does {topic} cost?", 0.85

        # Generic conversion - lower confidence
        return f"What is {query}?", 0.6

    def _detect_intent(self, query: str) -> str:
        """Detect search intent from query"""
        query_lower = query.lower()

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent

        return "informational"  # Default

    def _check_branded(self, query: str, brand_names: List[str]) -> bool:
        """Check if query contains brand name"""
        query_lower = query.lower()
        return any(brand.lower() in query_lower for brand in brand_names)

    def cluster_prompts(
        self,
        prompts: List[ConvertedPrompt],
        similarity_threshold: float = 0.7,
    ) -> List[PromptCluster]:
        """
        Cluster semantically similar prompts.

        In production, this would use embeddings (e.g., OpenAI embeddings)
        to cluster similar prompts together.
        """
        # Simple keyword-based clustering for now
        # Production would use sentence embeddings

        clusters: Dict[str, List[ConvertedPrompt]] = {}

        for prompt in prompts:
            # Extract main topic words
            words = set(prompt.original_query.lower().split())
            # Remove common words
            stop_words = {"the", "a", "an", "is", "are", "what", "how", "best", "top"}
            topic_words = words - stop_words

            # Find or create cluster
            cluster_key = self._find_matching_cluster(topic_words, clusters)
            if cluster_key:
                clusters[cluster_key].append(prompt)
            else:
                # Create new cluster
                cluster_name = " ".join(sorted(list(topic_words)[:3]))
                clusters[cluster_name] = [prompt]

        # Convert to PromptCluster objects
        result = []
        for i, (name, cluster_prompts) in enumerate(clusters.items()):
            total_impressions = sum(p.gsc_metrics.impressions for p in cluster_prompts)
            total_clicks = sum(p.gsc_metrics.clicks for p in cluster_prompts)
            avg_position = sum(p.gsc_metrics.position for p in cluster_prompts) / len(cluster_prompts)

            # Update cluster_id on prompts
            for p in cluster_prompts:
                p.cluster_id = i

            result.append(PromptCluster(
                id=i,
                name=name.title(),
                prompts=cluster_prompts,
                total_impressions=total_impressions,
                total_clicks=total_clicks,
                avg_position=avg_position,
            ))

        # Sort by traffic potential
        result.sort(key=lambda c: c.total_impressions, reverse=True)

        return result

    def _find_matching_cluster(
        self,
        topic_words: set,
        clusters: Dict[str, List],
    ) -> Optional[str]:
        """Find existing cluster that matches topic words"""
        for cluster_name in clusters:
            cluster_words = set(cluster_name.split())
            overlap = len(topic_words & cluster_words)
            if overlap >= 2 or (overlap == 1 and len(topic_words) <= 2):
                return cluster_name
        return None

    def prioritize_prompts(
        self,
        prompts: List[ConvertedPrompt],
        already_visible: List[str] = None,
    ) -> Dict[str, List[ConvertedPrompt]]:
        """
        Categorize prompts by visibility status and potential.

        Returns:
            {
                "already_visible": [...],  # Where client is cited
                "high_potential": [...],   # Strong GSC, not tested in AI
                "medium_potential": [...], # Moderate opportunity
                "low_priority": [...],     # Lower traffic potential
            }
        """
        already_visible = already_visible or []
        already_visible_lower = [p.lower() for p in already_visible]

        categories = {
            "already_visible": [],
            "high_potential": [],
            "medium_potential": [],
            "low_priority": [],
        }

        for prompt in prompts:
            # Check if already visible
            if prompt.conversational_prompt.lower() in already_visible_lower:
                categories["already_visible"].append(prompt)
                continue

            # Score based on GSC metrics
            score = self._calculate_potential_score(prompt)

            if score >= 80:
                categories["high_potential"].append(prompt)
            elif score >= 50:
                categories["medium_potential"].append(prompt)
            else:
                categories["low_priority"].append(prompt)

        # Sort each category by potential
        for cat in categories:
            categories[cat].sort(
                key=lambda p: self._calculate_potential_score(p),
                reverse=True,
            )

        return categories

    def _calculate_potential_score(self, prompt: ConvertedPrompt) -> float:
        """Calculate potential score for a prompt (0-100)"""
        metrics = prompt.gsc_metrics

        # Factors:
        # - Impressions (more = higher potential)
        # - Position (lower = easier to maintain in AI)
        # - Click-through rate (higher = more intent)
        # - Conversion confidence (higher = better prompt quality)

        impression_score = min(100, metrics.impressions / 100)  # Cap at 10k impressions
        position_score = max(0, 100 - (metrics.position * 2))  # Position 1 = 98, Position 50 = 0
        ctr_score = min(100, metrics.ctr * 1000)  # 10% CTR = 100
        confidence_score = prompt.conversion_confidence * 100

        weighted_score = (
            impression_score * 0.3 +
            position_score * 0.3 +
            ctr_score * 0.2 +
            confidence_score * 0.2
        )

        return weighted_score

    def generate_stakeholder_summary(
        self,
        categorized_prompts: Dict[str, List[ConvertedPrompt]],
    ) -> Dict:
        """Generate summary for stakeholder reporting"""
        visible_count = len(categorized_prompts["already_visible"])
        high_potential_count = len(categorized_prompts["high_potential"])
        total_prompts = sum(len(p) for p in categorized_prompts.values())

        total_impressions = sum(
            p.gsc_metrics.impressions
            for prompts in categorized_prompts.values()
            for p in prompts
        )

        high_potential_impressions = sum(
            p.gsc_metrics.impressions
            for p in categorized_prompts["high_potential"]
        )

        return {
            "headline": f"You're currently visible for {visible_count} AI prompts",
            "expansion_opportunity": f"Expansion opportunities: {high_potential_count} high-potential prompts identified",
            "stats": {
                "visible_prompts": visible_count,
                "high_potential_prompts": high_potential_count,
                "total_prompts_analyzed": total_prompts,
                "total_monthly_impressions": total_impressions,
                "potential_impressions_to_capture": high_potential_impressions,
            },
            "top_opportunities": [
                {
                    "prompt": p.conversational_prompt,
                    "monthly_impressions": p.gsc_metrics.impressions,
                    "current_position": p.gsc_metrics.position,
                }
                for p in categorized_prompts["high_potential"][:5]
            ],
        }
