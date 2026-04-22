"""Tests for the pure RRF math — no DB, no network."""
from app.services.rrf_calculator import RRFCalculatorService, SubQueryRank


def test_single_contribution_formula() -> None:
    rrf = RRFCalculatorService()
    # rank=0 is invalid → 0; rank 1 = 1/(60+1)
    assert rrf.calculate_single_contribution(0) == 0
    assert abs(rrf.calculate_single_contribution(1) - 1 / 61) < 1e-9


def test_quick_reference_meets_threshold() -> None:
    rrf = RRFCalculatorService()
    table = rrf.get_quick_reference_table()
    assert any(row["meets_threshold"] for row in table)
    # 2x at rank <=40 should meet threshold
    two_x = next(row for row in table if row["appearances"] == 2)
    assert two_x["meets_threshold"] is True


def test_calculate_from_sub_queries() -> None:
    rrf = RRFCalculatorService()
    queries = [
        SubQueryRank(query="a", rank=5, url="u"),
        SubQueryRank(query="b", rank=12, url="u"),
    ]
    result = rrf.calculate_from_sub_queries(queries)
    assert result.total_appearances == 2
    assert result.best_rank == 5
    assert result.worst_rank == 12
    assert result.raw_score > 0
