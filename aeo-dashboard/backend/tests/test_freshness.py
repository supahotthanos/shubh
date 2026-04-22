"""Freshness scoring math — no network."""
from app.services.freshness_analyzer import FreshnessAnalyzerService, FreshnessGrade


def test_score_fresh_recent_is_high() -> None:
    svc = FreshnessAnalyzerService()
    score = svc._calculate_freshness_score(10)
    assert score >= 95


def test_score_very_old_is_low() -> None:
    svc = FreshnessAnalyzerService()
    score = svc._calculate_freshness_score(1000)
    assert score < 20


def test_grades() -> None:
    svc = FreshnessAnalyzerService()
    assert svc._determine_grade(95) == FreshnessGrade.A
    assert svc._determine_grade(70) == FreshnessGrade.B
    assert svc._determine_grade(50) == FreshnessGrade.C
    assert svc._determine_grade(30) == FreshnessGrade.D
    assert svc._determine_grade(5) == FreshnessGrade.F
