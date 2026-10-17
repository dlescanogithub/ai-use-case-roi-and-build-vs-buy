from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.case import load_case
from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.build_vs_buy.matrix import load_scores, load_weights, score_matrix
from roi_and_build_vs_buy.build_vs_buy.sensitivity import analyze, shifted_weights

ROOT = Path(__file__).resolve().parents[1]


def test_bruma_ranking_matches_hand_total() -> None:
    case = load_case(ROOT / "examples" / "bruma_freight")
    ranking = score_matrix(case.weights, case.scores)
    assert ranking.order == ("build", "vendor_a", "vendor_b")
    assert ranking.winner.total == Decimal("3.70")
    assert ranking.ranked[1].total == Decimal("3.62")
    assert ranking.ranked[2].total == Decimal("3.02")


def test_cedro_ranking_matches_hand_total() -> None:
    case = load_case(ROOT / "examples" / "cedro_records")
    ranking = score_matrix(case.weights, case.scores)
    assert ranking.winner.option_id == "build"
    assert ranking.winner.total == Decimal("4.36")


def test_weights_must_sum_to_one(tmp_path: Path) -> None:
    path = tmp_path / "weights.yaml"
    path.write_text(
        "\n".join(
            [
                "case_id: sample",
                "org: Sample Co-op",
                "title: Sample",
                "as_of: '2026-10-17'",
                "fictional: true",
                "weights:",
                "  control: '0.50'",
                "  time_to_value: '0.50'",
                "  tco_3y: '0.10'",
                "  vendor_risk: '0.10'",
                "  security_compliance: '0.10'",
                "  maintainability: '0.10'",
                "  extensibility: '0.10'",
                "  exit_cost: '0.10'",
            ]
        ),
        encoding="utf-8",
    )
    try:
        load_weights(path)
    except ValidationError as exc:
        assert any("sum to 1" in item for item in exc.errors)
    else:
        raise AssertionError("expected a weight-sum failure")


def test_score_out_of_range_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "scores.yaml"
    path.write_text(
        "\n".join(
            [
                "case_id: sample",
                "options:",
                "  - id: build",
                "    label: Build",
                "    cells:",
                "      control: {score: 9, rationale: this rationale is long enough to pass}",
            ]
        ),
        encoding="utf-8",
    )
    try:
        load_scores(path)
    except ValidationError as exc:
        assert exc.errors
    else:
        raise AssertionError("expected a score failure")


def test_bruma_sensitivity_can_flip_the_winner() -> None:
    case = load_case(ROOT / "examples" / "bruma_freight")
    ranking = score_matrix(case.weights, case.scores)
    sensitivity = analyze(ranking, case.scores)
    assert Decimal(0) <= sensitivity.rank_stability_pct <= Decimal(100)
    assert Decimal(0) <= sensitivity.winner_stability_pct <= Decimal(100)
    flips = [item for item in sensitivity.flips if item.criterion == "time_to_value"]
    assert any(item.direction == "increase" and item.new_winner == "vendor_a" for item in flips)
    shifted = shifted_weights(dict(case.weights.weights), "time_to_value", Decimal("0.25"))
    assert shifted is not None
    assert sum(shifted.values(), Decimal(0)) == Decimal(1)
    assert shifted_weights(dict(case.weights.weights), "control", Decimal("0.95")) is None
