"""Weighted decision matrix. A higher score is better on every criterion."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.build_vs_buy.quantities import parse_decimal
from roi_and_build_vs_buy.build_vs_buy.yaml_io import load_mapping

CRITERIA: tuple[str, ...] = (
    "control",
    "time_to_value",
    "tco_3y",
    "vendor_risk",
    "security_compliance",
    "maintainability",
    "extensibility",
    "exit_cost",
)

CRITERION_LABELS: dict[str, str] = {
    "control": "Control",
    "time_to_value": "Time to value",
    "tco_3y": "3-year TCO",
    "vendor_risk": "Vendor risk",
    "security_compliance": "Security and compliance",
    "maintainability": "Maintainability",
    "extensibility": "Extensibility",
    "exit_cost": "Exit cost",
}

_WEIGHT_TOLERANCE = Decimal("0.000001")
_SCORE_MIN = 1
_SCORE_MAX = 5
_RATIONALE_MIN = 20


@dataclass(frozen=True)
class ScoreCell:
    """One criterion score and the human rationale that produced it.

    `estimate` true means the score is illustrative [EST], not a measured fact.
    """

    score: int
    rationale: str
    estimate: bool = False


@dataclass(frozen=True)
class OptionInput:
    """Scores for one option, before weighting."""

    option_id: str
    label: str
    cells: dict[str, ScoreCell]


@dataclass(frozen=True)
class Weights:
    """Criterion weights. They must sum to 1."""

    case_id: str
    org: str
    title: str
    as_of: str
    fictional: bool
    weights: dict[str, Decimal]


@dataclass(frozen=True)
class ScoreSheet:
    """All options for a case."""

    case_id: str
    options: tuple[OptionInput, ...]


@dataclass(frozen=True)
class RankedOption:
    """An option after weighting."""

    option_id: str
    label: str
    cells: dict[str, ScoreCell]
    total: Decimal


@dataclass(frozen=True)
class Ranking:
    """Options ordered from the highest weighted score to the lowest."""

    case_id: str
    weights: dict[str, Decimal]
    ranked: tuple[RankedOption, ...]

    @property
    def winner(self) -> RankedOption:
        return self.ranked[0]

    @property
    def order(self) -> tuple[str, ...]:
        return tuple(item.option_id for item in self.ranked)


def load_weights(path: Path) -> Weights:
    """Load and validate a weights file."""

    raw = load_mapping(path)
    case_id = _require_str(raw, "case_id", path.name)
    org = _require_str(raw, "org", path.name)
    title = _require_str(raw, "title", path.name)
    as_of = _require_str(raw, "as_of", path.name)
    _require_fictional(raw, path.name)
    weight_node = raw.get("weights")
    if not isinstance(weight_node, dict):
        raise ValidationError([f"{path.name} weights must be a mapping"])
    weights = _parse_weights(weight_node)
    return Weights(
        case_id=case_id,
        org=org,
        title=title,
        as_of=as_of,
        fictional=True,
        weights=weights,
    )


def load_scores(path: Path) -> ScoreSheet:
    """Load and validate a score sheet."""

    raw = load_mapping(path)
    case_id = _require_str(raw, "case_id", path.name)
    options_node = raw.get("options")
    if not isinstance(options_node, list) or not options_node:
        raise ValidationError([f"{path.name} options must be a non-empty list"])
    options: list[OptionInput] = []
    seen: set[str] = set()
    for index, item in enumerate(options_node):
        if not isinstance(item, dict):
            raise ValidationError([f"{path.name} options[{index}] must be a mapping"])
        option_id = _require_str(item, "id", f"{path.name} options[{index}]")
        label = _require_str(item, "label", f"{path.name} options[{index}]")
        if option_id in seen:
            raise ValidationError([f"duplicate option id {option_id}"])
        seen.add(option_id)
        cells = _parse_cells(item.get("cells"), f"{path.name} options[{index}]")
        options.append(OptionInput(option_id=option_id, label=label, cells=cells))
    return ScoreSheet(case_id=case_id, options=tuple(options))


def score_matrix(weights: Weights, sheet: ScoreSheet) -> Ranking:
    """Weight each option and rank them. Ties break by option id."""

    if weights.case_id != sheet.case_id:
        raise ValidationError([f"case_id mismatch: weights {weights.case_id} vs scores {sheet.case_id}"])
    ranked = [
        RankedOption(
            option_id=option.option_id,
            label=option.label,
            cells=option.cells,
            total=_weighted_total(option.cells, weights.weights),
        )
        for option in sheet.options
    ]
    ranked.sort(key=lambda item: (-item.total, item.option_id))
    return Ranking(case_id=weights.case_id, weights=dict(weights.weights), ranked=tuple(ranked))


def score_with_weights(
    weight_map: dict[str, Decimal],
    sheet: ScoreSheet,
    *,
    case_id: str,
) -> Ranking:
    """Rank `sheet` with an alternate weight map that already sums to 1."""

    validate_weight_map(weight_map)
    holder = Weights(
        case_id=case_id,
        org="",
        title="",
        as_of="",
        fictional=True,
        weights=weight_map,
    )
    return score_matrix(holder, sheet)


def validate_weight_map(weights: dict[str, Decimal]) -> None:
    """Reject a weight map that misses a criterion or does not sum to 1."""

    missing = [name for name in CRITERIA if name not in weights]
    extra = [name for name in weights if name not in CRITERIA]
    errors: list[str] = []
    if missing:
        errors.append("missing weights: " + ", ".join(missing))
    if extra:
        errors.append("unknown weights: " + ", ".join(sorted(extra)))
    for name, weight in weights.items():
        if name in CRITERIA and (weight <= 0 or weight >= 1):
            errors.append(f"weight {name} must be between 0 and 1 exclusive")
    total = sum(weights.get(name, Decimal(0)) for name in CRITERIA)
    if abs(total - Decimal(1)) > _WEIGHT_TOLERANCE:
        errors.append(f"weights must sum to 1 (got {total})")
    if errors:
        raise ValidationError(errors)


def _parse_weights(node: dict[object, object]) -> dict[str, Decimal]:
    parsed: dict[str, Decimal] = {}
    extra: list[str] = []
    for key, value in node.items():
        if not isinstance(key, str):
            raise ValidationError(["weight keys must be strings"])
        if key not in CRITERIA:
            extra.append(key)
            continue
        parsed[key] = parse_decimal(value, f"weights.{key}")
    if extra:
        raise ValidationError(["unknown weights: " + ", ".join(sorted(extra))])
    validate_weight_map(parsed)
    return parsed


def _parse_cells(node: object, path: str) -> dict[str, ScoreCell]:
    if not isinstance(node, dict):
        raise ValidationError([f"{path}.cells must be a mapping"])
    cells: dict[str, ScoreCell] = {}
    extra: list[str] = []
    for key, value in node.items():
        if not isinstance(key, str):
            raise ValidationError([f"{path}.cells has a non-string key"])
        if key not in CRITERIA:
            extra.append(key)
            continue
        cells[key] = _parse_cell(value, f"{path}.cells.{key}")
    errors: list[str] = []
    if extra:
        errors.append(f"{path} has unknown criteria: {', '.join(sorted(extra))}")
    missing = [name for name in CRITERIA if name not in cells]
    if missing:
        errors.append(f"{path} is missing criteria: {', '.join(missing)}")
    if errors:
        raise ValidationError(errors)
    return cells


def _parse_cell(node: object, path: str) -> ScoreCell:
    if not isinstance(node, dict):
        raise ValidationError([f"{path} must be a mapping"])
    score = node.get("score")
    rationale = node.get("rationale")
    errors: list[str] = []
    if isinstance(score, bool) or not isinstance(score, int):
        errors.append(f"{path}.score must be an integer from {_SCORE_MIN} to {_SCORE_MAX}")
        score = 0
    elif score < _SCORE_MIN or score > _SCORE_MAX:
        errors.append(f"{path}.score must be from {_SCORE_MIN} to {_SCORE_MAX}")
    if not isinstance(rationale, str) or len(rationale.strip()) < _RATIONALE_MIN:
        errors.append(f"{path}.rationale must be at least {_RATIONALE_MIN} characters")
        rationale = ""
    estimate = node.get("estimate", False)
    if not isinstance(estimate, bool):
        errors.append(f"{path}.estimate must be true or false")
        estimate = False
    if errors:
        raise ValidationError(errors)
    return ScoreCell(score=score, rationale=rationale.strip(), estimate=estimate)


def _weighted_total(cells: dict[str, ScoreCell], weights: dict[str, Decimal]) -> Decimal:
    total = Decimal(0)
    for name in CRITERIA:
        total += weights[name] * Decimal(cells[name].score)
    return total


def _require_str(node: dict[str, object], key: str, path: str) -> str:
    value = node.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError([f"{path} {key} must be a non-empty string"])
    return value.strip()


def _require_fictional(node: dict[str, object], path: str) -> None:
    if node.get("fictional") is not True:
        raise ValidationError([f"{path} must set fictional: true"])
