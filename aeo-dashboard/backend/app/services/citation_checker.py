"""
Citation Checker Service

Checks AI platforms for brand citations in response to prompts.
Supports multiple platforms: ChatGPT, Perplexity, Claude, Google AI, etc.
"""

import asyncio
import hashlib
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class CitationResult:
    was_cited: bool
    position: Optional[int]  # 1 = first mention
    cited_url: Optional[str]
    cited_text: Optional[str]
    mention_type: str  # "linked", "unlinked", "brand_mention"
    context_snippet: Optional[str]
    confidence_score: float
    response_text: str
    response_hash: str
    model_version: Optional[str]
    check_duration_ms: int


@dataclass
class MultiCheckResult:
    """Result of checking a prompt multiple times for variance"""
    prompt_text: str
    platform: str
    check_count: int
    citation_rate: float  # % of checks where brand was cited
    avg_position: Optional[float]
    position_variance: float
    is_stable: bool  # True if citation_rate > 80%
    results: List[CitationResult]


class BasePlatformChecker(ABC):
    """Base class for platform-specific citation checkers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    async def check_citation(
        self,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
    ) -> CitationResult:
        """Check if the brand is cited in response to a prompt"""
        pass

    def _find_brand_mentions(
        self,
        text: str,
        brand_names: List[str],
        brand_urls: List[str],
    ) -> Tuple[bool, Optional[int], str, Optional[str]]:
        """
        Find brand mentions in text.

        Returns:
            (was_cited, position, mention_type, cited_text)
        """
        text_lower = text.lower()

        # Check for URL mentions (linked)
        for url in brand_urls:
            domain = self._extract_domain(url)
            if domain.lower() in text_lower or url.lower() in text_lower:
                position = self._find_mention_position(text, domain)
                return True, position, "linked", domain

        # Check for brand name mentions (unlinked)
        for brand in brand_names:
            if brand.lower() in text_lower:
                position = self._find_mention_position(text, brand)
                return True, position, "unlinked", brand

        return False, None, "none", None

    def _find_mention_position(self, text: str, term: str) -> int:
        """Find which mention number this is (1st, 2nd, etc.)"""
        text_lower = text.lower()
        term_lower = term.lower()

        # Split into sentences/chunks and find position
        sentences = re.split(r'[.!?\n]', text)
        for i, sentence in enumerate(sentences, 1):
            if term_lower in sentence.lower():
                return i

        return 1

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        url = url.replace("https://", "").replace("http://", "")
        url = url.replace("www.", "")
        return url.split("/")[0]

    def _get_context_snippet(self, text: str, term: str, window: int = 200) -> str:
        """Extract context around the mention"""
        text_lower = text.lower()
        term_lower = term.lower()

        idx = text_lower.find(term_lower)
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(term) + window)

        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def _hash_response(self, text: str) -> str:
        """Generate hash of response for change detection"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]


class OpenAICitationChecker(BasePlatformChecker):
    """Check citations in ChatGPT/OpenAI responses"""

    PLATFORM = "chatgpt"
    DEFAULT_MODEL = "gpt-4-turbo"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = None  # Will be initialized with OpenAI client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def check_citation(
        self,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
    ) -> CitationResult:
        """Check if brand is cited in ChatGPT response"""
        import time
        start_time = time.time()

        try:
            # This would use the actual OpenAI API
            # For now, we'll structure the expected flow
            response_text = await self._call_openai_api(prompt, model, temperature)

            duration_ms = int((time.time() - start_time) * 1000)

            was_cited, position, mention_type, cited_text = self._find_brand_mentions(
                response_text, brand_names, brand_urls
            )

            context = None
            confidence = 0.0
            if was_cited and cited_text:
                context = self._get_context_snippet(response_text, cited_text)
                # Higher confidence for linked mentions
                confidence = 0.95 if mention_type == "linked" else 0.85

            return CitationResult(
                was_cited=was_cited,
                position=position,
                cited_url=brand_urls[0] if was_cited and mention_type == "linked" else None,
                cited_text=cited_text,
                mention_type=mention_type,
                context_snippet=context,
                confidence_score=confidence,
                response_text=response_text,
                response_hash=self._hash_response(response_text),
                model_version=model,
                check_duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return CitationResult(
                was_cited=False,
                position=None,
                cited_url=None,
                cited_text=None,
                mention_type="error",
                context_snippet=str(e),
                confidence_score=0.0,
                response_text="",
                response_hash="",
                model_version=model,
                check_duration_ms=duration_ms,
            )

    async def _call_openai_api(
        self, prompt: str, model: str, temperature: float
    ) -> str:
        """Make actual API call to OpenAI"""
        # Placeholder for actual OpenAI API integration
        # In production, this would use the openai package
        raise NotImplementedError("OpenAI API integration required")


class AnthropicCitationChecker(BasePlatformChecker):
    """Check citations in Claude responses"""

    PLATFORM = "claude"
    DEFAULT_MODEL = "claude-3-opus-20240229"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def check_citation(
        self,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
        model: str = DEFAULT_MODEL,
    ) -> CitationResult:
        """Check if brand is cited in Claude response"""
        import time
        start_time = time.time()

        try:
            response_text = await self._call_anthropic_api(prompt, model)
            duration_ms = int((time.time() - start_time) * 1000)

            was_cited, position, mention_type, cited_text = self._find_brand_mentions(
                response_text, brand_names, brand_urls
            )

            context = None
            confidence = 0.0
            if was_cited and cited_text:
                context = self._get_context_snippet(response_text, cited_text)
                confidence = 0.95 if mention_type == "linked" else 0.85

            return CitationResult(
                was_cited=was_cited,
                position=position,
                cited_url=brand_urls[0] if was_cited and mention_type == "linked" else None,
                cited_text=cited_text,
                mention_type=mention_type,
                context_snippet=context,
                confidence_score=confidence,
                response_text=response_text,
                response_hash=self._hash_response(response_text),
                model_version=model,
                check_duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return CitationResult(
                was_cited=False,
                position=None,
                cited_url=None,
                cited_text=None,
                mention_type="error",
                context_snippet=str(e),
                confidence_score=0.0,
                response_text="",
                response_hash="",
                model_version=model,
                check_duration_ms=duration_ms,
            )

    async def _call_anthropic_api(self, prompt: str, model: str) -> str:
        """Make actual API call to Anthropic"""
        raise NotImplementedError("Anthropic API integration required")


class PerplexityCitationChecker(BasePlatformChecker):
    """Check citations in Perplexity responses (via web scraping or API)"""

    PLATFORM = "perplexity"

    async def check_citation(
        self,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
    ) -> CitationResult:
        """Check if brand is cited in Perplexity response"""
        # Perplexity checking would typically use their API or BrightData scraping
        raise NotImplementedError("Perplexity API integration required")


class CitationCheckerService:
    """
    Main service for checking citations across multiple AI platforms.
    """

    def __init__(
        self,
        openai_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        brightdata_key: Optional[str] = None,
    ):
        self.checkers: Dict[str, BasePlatformChecker] = {}

        if openai_key:
            self.checkers["chatgpt"] = OpenAICitationChecker(openai_key)
        if anthropic_key:
            self.checkers["claude"] = AnthropicCitationChecker(anthropic_key)

    async def check_single_platform(
        self,
        platform: str,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
    ) -> CitationResult:
        """Check citation on a single platform"""
        if platform not in self.checkers:
            raise ValueError(f"Platform {platform} not configured")

        return await self.checkers[platform].check_citation(
            prompt, brand_names, brand_urls
        )

    async def check_all_platforms(
        self,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, CitationResult]:
        """Check citation across all configured platforms"""
        platforms = platforms or list(self.checkers.keys())

        tasks = [
            self.check_single_platform(platform, prompt, brand_names, brand_urls)
            for platform in platforms
            if platform in self.checkers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            platform: result
            for platform, result in zip(platforms, results)
            if not isinstance(result, Exception)
        }

    async def check_with_variance(
        self,
        platform: str,
        prompt: str,
        brand_names: List[str],
        brand_urls: List[str],
        check_count: int = 10,
    ) -> MultiCheckResult:
        """
        Check citation multiple times to assess stability.

        AI responses can vary due to temperature settings.
        Running multiple checks helps assess true visibility.
        """
        results = []

        for _ in range(check_count):
            result = await self.check_single_platform(
                platform, prompt, brand_names, brand_urls
            )
            results.append(result)
            # Small delay between checks
            await asyncio.sleep(0.5)

        # Calculate metrics
        cited_count = sum(1 for r in results if r.was_cited)
        citation_rate = cited_count / check_count

        positions = [r.position for r in results if r.position is not None]
        avg_position = sum(positions) / len(positions) if positions else None

        # Calculate variance
        if len(positions) > 1:
            mean = sum(positions) / len(positions)
            variance = sum((p - mean) ** 2 for p in positions) / len(positions)
        else:
            variance = 0.0

        return MultiCheckResult(
            prompt_text=prompt,
            platform=platform,
            check_count=check_count,
            citation_rate=citation_rate,
            avg_position=avg_position,
            position_variance=variance,
            is_stable=citation_rate >= 0.8,
            results=results,
        )

    def calculate_stability_score(
        self, check_results: List[CitationResult]
    ) -> float:
        """
        Calculate citation stability score (0-100).

        100 = Always cited in same position
        0 = Never cited or highly variable
        """
        if not check_results:
            return 0.0

        cited_count = sum(1 for r in check_results if r.was_cited)
        citation_rate = cited_count / len(check_results)

        if citation_rate == 0:
            return 0.0

        # Factor in position consistency
        positions = [r.position for r in check_results if r.position is not None]
        if not positions:
            return citation_rate * 50  # Half score if no position data

        # Position consistency (lower variance = higher score)
        if len(positions) > 1:
            mean = sum(positions) / len(positions)
            variance = sum((p - mean) ** 2 for p in positions) / len(positions)
            position_consistency = max(0, 1 - (variance / 10))  # Normalize
        else:
            position_consistency = 1.0

        # Combined score
        return (citation_rate * 0.7 + position_consistency * 0.3) * 100
