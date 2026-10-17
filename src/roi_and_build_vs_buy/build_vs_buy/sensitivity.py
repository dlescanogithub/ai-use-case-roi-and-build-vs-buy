"""Weight perturbation, rank stability, and the smallest change that flips the winner."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from roi_and_build_vs_buy.build_vs_buy.matrix import Ranking, ScoreSheet, score_with_weights

PERTURB_STEPS: tuple[Decimal, ...] = (
    Decimal("-0.10"),
    Decimal("-0.05"),
    Decimal("0.05"),
    Decimal("0.10"),
)
_FLIP_STEP = Decimal("0.001")
_MIN_WEIGHT = Decimal("0.01")
_MAX_WEIGHT = Decimal("0.90")


@dataclass(frozen=True)
class Perturbation:
    """One feasible one-at-a-time weight shift."""

    criterion: str
    delta: Decimal
    winner: str
    order: tuple[str, ...]
    full_rank_held: bool
    winner_held: bool


@dataclass(frozen=True)
class Flip:
    """Smallest absolute weight change, searched at 0.001 resolution, that flips the winner."""

    criterion: str
    direction: str
    delta: Decimal
    new_weight: Decimal
    new_winner: str


@dataclass(frozen=True)
class Sensitivity:
    """Stability of a ranking under weight perturbation."""

    baseline_winner: str
    baseline_order: tuple[str, ...]
    scenarios: tuple[Perturbation, ...]
    rank_stability_pct: Decimal
    winner_stability_pct: Decimal
    flips: tuple[Flip, ...]


def analyze(ranking: Ranking, sheet: ScoreSheet) -> Sensitivity:
    """Perturb each weight, renormalize, and search for flip thresholds."""

    scenarios: list[Perturbation] = []
    for criterion in ranking.weights:
        for delta in PERTURB_STEPS:
            shifted = shifted_weights(ranking.weights, criterion, ranking.weights[criterion] + delta)
            if shifted is None:
                continue
            scored = score_with_weights(shifted, sheet, case_id=ranking.case_id)
            scenarios.append(
                Perturbation(
                    criterion=criterion,
                    delta=delta,
                    winner=scored.winner.option_id,
                    order=scored.order,
                    full_rank_held=scored.order == ranking.order,
                    winner_held=scored.winner.option_id == ranking.winner.option_id,
                )
            )
    total = len(scenarios)
    if total == 0:
        rank_pct = Decimal(0)
        winner_pct = Decimal(0)
    else:
        rank_pct = (Decimal(sum(1 for item in scenarios if item.full_rank_held)) / Decimal(total)) * 100
        winner_pct = (Decimal(sum(1 for item in scenarios if item.winner_held)) / Decimal(total)) * 100
    flips: list[Flip] = []
    for criterion in ranking.weights:
        for sign in (Decimal(1), Decimal(-1)):
            found = _smallest_flip(ranking, sheet, criterion, sign)
            if found is not None:
                flips.append(found)
    return Sensitivity(
        baseline_winner=ranking.winner.option_id,
        baseline_order=ranking.order,
        scenarios=tuple(scenarios),
        rank_stability_pct=rank_pct.quantize(Decimal("0.01")),
        winner_stability_pct=winner_pct.quantize(Decimal("0.01")),
        flips=tuple(flips),
    )


def shifted_weights(
    weights: dict[str, Decimal],
    criterion: str,
    new_weight: Decimal,
) -> dict[str, Decimal] | None:
    """Move one weight and scale the others so the map still sums to 1.

    Returns None when the new weight leaves the feasible band, or when another
    weight would fall to zero or below.
    """

    if new_weight < _MIN_WEIGHT or new_weight > _MAX_WEIGHT:
        return None
    old = weights[criterion]
    rest = Decimal(1) - old
    if rest <= 0:
        return None
    scale = (Decimal(1) - new_weight) / rest
    others = [key for key in weights if key != criterion]
    if not others:
        return None
    shifted: dict[str, Decimal] = {criterion: new_weight}
    consumed = new_weight
    for key in others[:-1]:
        scaled = weights[key] * scale
        if scaled <= 0:
            return None
        shifted[key] = scaled
        consumed += scaled
    last = Decimal(1) - consumed
    if last <= 0:
        return None
    shifted[others[-1]] = last
    return shifted


def _smallest_flip(
    ranking: Ranking,
    sheet: ScoreSheet,
    criterion: str,
    sign: Decimal,
) -> Flip | None:
    current = ranking.weights[criterion]
    delta = _FLIP_STEP
    while True:
        candidate = current + (sign * delta)
        if candidate < _MIN_WEIGHT or candidate > _MAX_WEIGHT:
            return None
        shifted = shifted_weights(ranking.weights, criterion, candidate)
        if shifted is None:
            return None
        scored = score_with_weights(shifted, sheet, case_id=ranking.case_id)
        if scored.winner.option_id != ranking.winner.option_id:
            direction = "increase" if sign > 0 else "decrease"
            return Flip(
                criterion=criterion,
                direction=direction,
                delta=delta,
                new_weight=candidate,
                new_winner=scored.winner.option_id,
            )
        delta += _FLIP_STEP
        if delta > Decimal(1):
            return None
