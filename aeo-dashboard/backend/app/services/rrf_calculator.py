"""
RRF (Reciprocal Rank Fusion) Score Calculator

Based on ChatGPT's k≈60 RRF system for combining multiple ranking signals.
Formula: RRF Score = Σ(1/(k + rank)) for all appearances

Target threshold: τ = 0.020 (likely in top-60 citation pool)
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class SubQueryRank:
    query: str
    rank: int
    url: str
    search_engine: str = "google"


@dataclass
class RRFResult:
    raw_score: float
    normalized_score: float
    meets_threshold: bool
    total_appearances: int
    avg_rank: float
    best_rank: int
    worst_rank: int
    appearances_needed: int
    target_rank_each: int
    breakdown: List[Dict]


class RRFCalculatorService:
    """
    Calculate RRF (Reciprocal Rank Fusion) scores for AI citation likelihood.

    The RRF formula combines rankings from multiple queries:
    RRF(d) = Σ 1/(k + r(d)) where k is a constant (60) and r(d) is the rank.

    Higher scores indicate higher likelihood of being in the AI's citation pool.
    """

    DEFAULT_K = 60.0
    DEFAULT_THRESHOLD = 0.020

    # Quick reference lookup table
    QUICK_REFERENCE = [
        {"appearances": 1, "max_rank": 1, "score": 0.0164},
        {"appearances": 2, "max_rank": 40, "score": 0.0200},
        {"appearances": 3, "max_rank": 90, "score": 0.0200},
        {"appearances": 4, "max_rank": 140, "score": 0.0200},
        {"appearances": 5, "max_rank": 190, "score": 0.0200},
    ]

    def __init__(self, k: float = DEFAULT_K, threshold: float = DEFAULT_THRESHOLD):
        self.k = k
        self.threshold = threshold

    def calculate_single_contribution(self, rank: int) -> float:
        """Calculate the RRF contribution of a single ranking."""
        if rank < 1:
            return 0.0
        return 1.0 / (self.k + rank)

    def calculate_rrf_score(self, ranks: List[int]) -> float:
        """
        Calculate the total RRF score from a list of rankings.

        Args:
            ranks: List of ranking positions (1-indexed)

        Returns:
            Total RRF score
        """
        if not ranks:
            return 0.0

        return sum(self.calculate_single_contribution(r) for r in ranks if r > 0)

    def calculate_from_sub_queries(
        self, sub_queries: List[SubQueryRank]
    ) -> RRFResult:
        """
        Calculate RRF score from a list of sub-query rankings.

        Args:
            sub_queries: List of SubQueryRank objects

        Returns:
            RRFResult with full breakdown
        """
        if not sub_queries:
            return RRFResult(
                raw_score=0.0,
                normalized_score=0.0,
                meets_threshold=False,
                total_appearances=0,
                avg_rank=0.0,
                best_rank=0,
                worst_rank=0,
                appearances_needed=self._calculate_appearances_needed(0.0),
                target_rank_each=40,
                breakdown=[],
            )

        ranks = [sq.rank for sq in sub_queries if sq.rank > 0]

        if not ranks:
            return RRFResult(
                raw_score=0.0,
                normalized_score=0.0,
                meets_threshold=False,
                total_appearances=0,
                avg_rank=0.0,
                best_rank=0,
                worst_rank=0,
                appearances_needed=self._calculate_appearances_needed(0.0),
                target_rank_each=40,
                breakdown=[],
            )

        raw_score = self.calculate_rrf_score(ranks)

        # Normalize to 0-1 scale (theoretical max is appearances * 1/61)
        max_possible = len(ranks) * self.calculate_single_contribution(1)
        normalized_score = raw_score / max_possible if max_possible > 0 else 0.0

        breakdown = [
            {
                "query": sq.query,
                "rank": sq.rank,
                "url": sq.url,
                "contribution": self.calculate_single_contribution(sq.rank),
                "search_engine": sq.search_engine,
            }
            for sq in sub_queries
        ]

        return RRFResult(
            raw_score=raw_score,
            normalized_score=normalized_score,
            meets_threshold=raw_score >= self.threshold,
            total_appearances=len(ranks),
            avg_rank=sum(ranks) / len(ranks),
            best_rank=min(ranks),
            worst_rank=max(ranks),
            appearances_needed=self._calculate_appearances_needed(raw_score),
            target_rank_each=self._calculate_target_rank(raw_score, len(ranks)),
            breakdown=breakdown,
        )

    def _calculate_appearances_needed(self, current_score: float) -> int:
        """Calculate how many more appearances needed to meet threshold."""
        if current_score >= self.threshold:
            return 0

        gap = self.threshold - current_score
        # Assume average rank of 40 for new appearances
        contribution_per_appearance = self.calculate_single_contribution(40)

        return math.ceil(gap / contribution_per_appearance)

    def _calculate_target_rank(
        self, current_score: float, current_appearances: int
    ) -> int:
        """Calculate what rank is needed for additional appearances."""
        if current_score >= self.threshold:
            return 100  # Any rank works

        gap = self.threshold - current_score
        # If we add one more appearance, what rank would we need?
        # gap = 1/(k + rank) => rank = 1/gap - k

        if gap <= 0:
            return 100

        target_rank = int((1.0 / gap) - self.k)
        return max(1, min(target_rank, 200))

    def get_recommendations(
        self, result: RRFResult, keyword: str
    ) -> Dict:
        """Generate actionable recommendations based on RRF analysis."""
        recommendations = {
            "keyword": keyword,
            "current_score": result.raw_score,
            "target_score": self.threshold,
            "gap": max(0, self.threshold - result.raw_score),
            "priority": "high" if result.raw_score < 0.010 else "medium" if result.raw_score < self.threshold else "low",
            "status": "meeting_threshold" if result.meets_threshold else "below_threshold",
            "action_items": [],
        }

        if result.meets_threshold:
            recommendations["recommendation"] = (
                f"Your content meets the RRF threshold ({result.raw_score:.4f} >= {self.threshold}). "
                f"Focus on maintaining rankings and expanding to new sub-queries."
            )
            recommendations["action_items"] = [
                "Monitor ranking stability weekly",
                "Identify related sub-queries for expansion",
                "Ensure content freshness to maintain positions",
            ]
        else:
            if result.total_appearances == 0:
                recommendations["recommendation"] = (
                    f"No rankings found for this keyword. "
                    f"Need to appear in at least 2 sub-queries at rank 40 or better."
                )
                recommendations["action_items"] = [
                    "Create comprehensive content targeting this topic",
                    "Build topical authority through supporting content",
                    "Acquire quality backlinks to boost rankings",
                ]
            elif result.total_appearances == 1:
                recommendations["recommendation"] = (
                    f"Only 1 appearance found. Need {result.appearances_needed} more appearance(s) "
                    f"at rank {result.target_rank_each} or better to meet threshold."
                )
                recommendations["action_items"] = [
                    f"Create content for related sub-queries",
                    f"Target rank {result.target_rank_each} or better",
                    "Optimize existing content for broader keyword coverage",
                ]
            else:
                recommendations["recommendation"] = (
                    f"Found {result.total_appearances} appearances (avg rank: {result.avg_rank:.0f}). "
                    f"Need {result.appearances_needed} more at rank {result.target_rank_each} or improve existing ranks."
                )
                recommendations["action_items"] = [
                    f"Improve worst-performing ranking (currently #{result.worst_rank})",
                    f"Target {result.appearances_needed} additional sub-queries",
                    "Focus on sub-queries where you're close to page 1",
                ]

        return recommendations

    def get_quick_reference_table(self) -> List[Dict]:
        """
        Get the quick reference table showing guaranteed scores.

        | Appearances | Max Rank Each | Guaranteed Score |
        |------------|---------------|------------------|
        | 2×         | ≤ 40          | 0.0200 ✓        |
        | 3×         | ≤ 90          | 0.0200 ✓        |
        | 4×         | ≤ 140         | 0.0200 ✓        |
        """
        table = []

        for appearances in range(1, 6):
            # Find max rank where score still meets threshold
            max_rank = self._find_max_rank_for_threshold(appearances)
            score = appearances * self.calculate_single_contribution(max_rank)

            table.append({
                "appearances": appearances,
                "max_rank_each": max_rank,
                "guaranteed_score": round(score, 4),
                "meets_threshold": score >= self.threshold,
                "description": f"{appearances}× at ≤{max_rank}" if max_rank < 200 else f"{appearances}× needed",
            })

        return table

    def _find_max_rank_for_threshold(self, appearances: int) -> int:
        """Find the maximum rank where N appearances still meet threshold."""
        target_per_appearance = self.threshold / appearances
        # 1/(k + rank) = target => rank = 1/target - k

        if target_per_appearance <= 0:
            return 200

        max_rank = int((1.0 / target_per_appearance) - self.k)
        return max(1, min(max_rank, 200))

    def simulate_improvement(
        self, current_result: RRFResult, new_rank: int
    ) -> Tuple[float, bool]:
        """
        Simulate adding one more appearance at a given rank.

        Returns:
            Tuple of (new_score, would_meet_threshold)
        """
        new_contribution = self.calculate_single_contribution(new_rank)
        new_score = current_result.raw_score + new_contribution
        return new_score, new_score >= self.threshold
