"""Invariant checks for a decision case.

This module is a regression test of the decision model. It checks properties
that must hold: weights sum to 1, the approved winner matches, cost stays at
zero, TCO moves monotonically, and the run records no external action. It does
not lock a tool-call transcript and it does not score an assistant.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.matrix import ScoreSheet, Weights, score_matrix
from roi_and_build_vs_buy.build_vs_buy.report import render_report
from roi_and_build_vs_buy.build_vs_buy.sensitivity import analyze
from roi_and_build_vs_buy.build_vs_buy.tco import TcoInput, probe_monotonicity
from roi_and_build_vs_buy.evalkit.prices import build_eval_provider
from roi_and_build_vs_buy.evalkit.prices.cassette import CassettePriceProvider
from roi_and_build_vs_buy.evalkit.trace import append_trace

_FORBIDDEN_ACTIONS = frozenset({"http_post", "send_email", "purchase", "provision", "scrape"})
_COST_CAP = Decimal(0)


def evaluate_case(
    *,
    case_id: str,
    weights: Weights,
    scores: ScoreSheet,
    model: TcoInput,
    cassette_path: Path,
    golden_winner: str,
    min_winner_stability_pct: Decimal,
    trace_path: Path,
    case_dir_display: str,
) -> list[str]:
    """Return a list of invariant failures. An empty list means the case passed."""

    failures: list[str] = []
    ranking = score_matrix(weights, scores)
    weight_sum = sum(ranking.weights.values(), Decimal(0))
    if weight_sum != Decimal(1):
        failures.append(f"weights_sum: expected 1 got {weight_sum}")
    if ranking.winner.option_id != golden_winner:
        failures.append(f"golden_winner: expected {golden_winner} got {ranking.winner.option_id}")
    sensitivity = analyze(ranking, scores)
    if sensitivity.winner_stability_pct < 0 or sensitivity.winner_stability_pct > 100:
        failures.append("winner_stability_pct out of range")
    if sensitivity.rank_stability_pct < 0 or sensitivity.rank_stability_pct > 100:
        failures.append("rank_stability_pct out of range")
    if sensitivity.winner_stability_pct < min_winner_stability_pct:
        failures.append(
            "winner_stability_pct "
            f"{sensitivity.winner_stability_pct} is below the approved floor "
            f"{min_winner_stability_pct}"
        )
    failures.extend(probe_monotonicity(model))
    provider = build_eval_provider(cassette_path)
    if not isinstance(provider, CassettePriceProvider):
        failures.append("eval provider must be the cassette provider")
    cost = Decimal(0)
    quoted: list[str] = []
    for spec in model.buy_options:
        quote = provider.quote(spec.option_id)
        quoted.append(spec.option_id)
        cost += quote.cost_usd
        if quote.simulated is not True:
            failures.append(f"quote {spec.option_id} is not simulated")
        if quote.cost_usd != 0:
            failures.append(f"quote {spec.option_id} charged a non-zero cost")
    if cost > _COST_CAP:
        failures.append(f"cost_cap: run cost {cost} exceeds {_COST_CAP}")
    report = render_report(
        ranking=ranking,
        sensitivity=sensitivity,
        model=model,
        case_dir=case_dir_display,
    )
    if "BEGIN PRIVATE KEY" in report or "BEGIN RSA PRIVATE KEY" in report:
        failures.append("harmful_effect: report contains key material")
    for action in _FORBIDDEN_ACTIONS:
        if action in report:
            failures.append(f"unapproved_external_action: report mentions {action}")
    if "simulated" not in report or "[EST]" not in report:
        failures.append("report must label simulated [EST] figures")
    append_trace(
        trace_path,
        {
            "case_id": case_id,
            "winner": ranking.winner.option_id,
            "winner_stability_pct": str(sensitivity.winner_stability_pct),
            "rank_stability_pct": str(sensitivity.rank_stability_pct),
            "external_action": False,
            "action": "write_report",
            "cost_usd": str(cost),
            "quoted_vendors": quoted,
            "failures": failures,
        },
    )
    if "write_report" in _FORBIDDEN_ACTIONS:
        failures.append("unapproved_external_action")
    return failures
