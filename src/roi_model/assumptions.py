"""Load and validate assumption files.

Every number in a case file is an assumption ([EST]) unless a separate
measured-cost file with ``status: measured`` overrides the per-run agent cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from roi_model.retry import retry

Distribution = Literal["triangular", "pert"]
CaseStatus = Literal["implemented", "design-only"]

SHARED_PARAMETERS = (
    "manual_minutes_per_item",
    "loaded_cost_per_hour",
    "manual_error_rate",
    "agent_error_rate",
    "cost_of_error",
    "input_tokens",
    "output_tokens",
    "input_price_per_million",
    "output_price_per_million",
    "review_minutes",
    "review_rate",
    "implementation_cost",
    "monthly_run_cost",
    "adoption_ramp_months",
    "discount_rate_annual",
)

DAILY_PARAMETERS = ("volume_per_day", "working_days_per_month", *SHARED_PARAMETERS)
MONTHLY_PARAMETERS = ("volume_per_month", *SHARED_PARAMETERS)

RATE_PARAMETERS = frozenset({"manual_error_rate", "agent_error_rate", "review_rate", "discount_rate_annual"})


class AssumptionError(ValueError):
    """The case file is not usable."""


@dataclass(frozen=True)
class Parameter:
    name: str
    value: float
    low: float
    high: float
    unit: str
    distribution: Distribution
    rationale: str
    illustrative: bool


@dataclass(frozen=True)
class CaseMeta:
    case_id: str
    title: str
    company: str
    status: CaseStatus
    fictional: bool
    currency: str
    narrative: str
    narrative_es: str
    horizon_months: int
    measured_cost_slot: str


@dataclass(frozen=True)
class Assumptions:
    """Flat numeric inputs for one evaluation."""

    volume_per_day: float | None
    volume_per_month: float | None
    working_days_per_month: float
    manual_minutes_per_item: float
    loaded_cost_per_hour: float
    manual_error_rate: float
    agent_error_rate: float
    cost_of_error: float
    input_tokens: float
    output_tokens: float
    input_price_per_million: float
    output_price_per_million: float
    agent_cost_per_run_override: float | None
    review_minutes: float
    review_rate: float
    implementation_cost: float
    monthly_run_cost: float
    adoption_ramp_months: float
    discount_rate_annual: float
    horizon_months: int
    currency: str
    case_id: str

    @property
    def agent_cost_per_run(self) -> float:
        if self.agent_cost_per_run_override is not None:
            return self.agent_cost_per_run_override
        return (
            self.input_tokens * self.input_price_per_million + self.output_tokens * self.output_price_per_million
        ) / 1_000_000


@dataclass(frozen=True)
class CaseFile:
    meta: CaseMeta
    parameters: dict[str, Parameter]
    scenarios: dict[str, dict[str, float]]
    volume_mode: Literal["daily", "monthly"]


def _mapping(raw: object, ctx: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise AssumptionError(f"{ctx} must be a mapping")
    out: dict[str, object] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise AssumptionError(f"{ctx} has a non-string key")
        out[key] = value
    return out


def _text(raw: object, ctx: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise AssumptionError(f"{ctx} must be a non-empty string")
    return raw.strip()


def _number(raw: object, ctx: str) -> float:
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise AssumptionError(f"{ctx} must be a number")
    value = float(raw)
    if value != value or value in (float("inf"), float("-inf")):
        raise AssumptionError(f"{ctx} must be finite")
    return value


def _read_yaml(path: Path) -> object:
    def _read() -> object:
        text = path.read_text(encoding="utf-8")
        loaded: object = yaml.safe_load(text)
        return loaded

    return retry(_read, max_attempts=3, base_delay=0.01, backoff_cap=0.05)


def validate_assumptions(assumptions: Assumptions) -> None:
    """Reject inputs that would make the formulas meaningless."""
    if (assumptions.volume_per_month is None) == (assumptions.volume_per_day is None):
        raise AssumptionError("set exactly one of volume_per_day or volume_per_month")
    if assumptions.volume_per_day is not None and assumptions.volume_per_day < 0:
        raise AssumptionError("volume_per_day must be >= 0")
    if assumptions.volume_per_month is not None and assumptions.volume_per_month < 0:
        raise AssumptionError("volume_per_month must be >= 0")
    if assumptions.volume_per_day is not None and not 0 < assumptions.working_days_per_month <= 31:
        raise AssumptionError("working_days_per_month must be in (0, 31]")
    non_negative = {
        "manual_minutes_per_item": assumptions.manual_minutes_per_item,
        "loaded_cost_per_hour": assumptions.loaded_cost_per_hour,
        "cost_of_error": assumptions.cost_of_error,
        "input_tokens": assumptions.input_tokens,
        "output_tokens": assumptions.output_tokens,
        "input_price_per_million": assumptions.input_price_per_million,
        "output_price_per_million": assumptions.output_price_per_million,
        "review_minutes": assumptions.review_minutes,
        "implementation_cost": assumptions.implementation_cost,
        "monthly_run_cost": assumptions.monthly_run_cost,
        "adoption_ramp_months": assumptions.adoption_ramp_months,
    }
    for name, value in non_negative.items():
        if value < 0:
            raise AssumptionError(f"{name} must be >= 0")
    rates = {
        "manual_error_rate": assumptions.manual_error_rate,
        "agent_error_rate": assumptions.agent_error_rate,
        "review_rate": assumptions.review_rate,
    }
    for name, value in rates.items():
        if not 0 <= value <= 1:
            raise AssumptionError(f"{name} must be between 0 and 1")
    if not 0 <= assumptions.discount_rate_annual < 1:
        raise AssumptionError("discount_rate_annual must be in [0, 1)")
    override = assumptions.agent_cost_per_run_override
    if override is not None and override < 0:
        raise AssumptionError("agent_cost_per_run override must be >= 0")
    if not 1 <= assumptions.horizon_months <= 600:
        raise AssumptionError("horizon_months must be between 1 and 600")
    if len(assumptions.currency) != 3 or not assumptions.currency.isalpha():
        raise AssumptionError("currency must be a 3-letter code")
    if not assumptions.currency.isupper():
        raise AssumptionError("currency must be uppercase")


def _parameter(name: str, raw: object) -> Parameter:
    body = _mapping(raw, name)
    expected = {"value", "low", "high", "unit", "distribution", "rationale", "illustrative"}
    missing = expected - set(body)
    extra = set(body) - expected
    if missing or extra:
        raise AssumptionError(f"{name} keys must be {sorted(expected)}")
    value = _number(body["value"], f"{name}.value")
    low = _number(body["low"], f"{name}.low")
    high = _number(body["high"], f"{name}.high")
    if not low <= value <= high:
        raise AssumptionError(f"{name} must satisfy low <= value <= high")
    unit = _text(body["unit"], f"{name}.unit")
    distribution = body["distribution"]
    if distribution not in {"triangular", "pert"}:
        raise AssumptionError(f"{name}.distribution must be triangular or pert")
    rationale = _text(body["rationale"], f"{name}.rationale")
    if "[EST]" not in rationale:
        raise AssumptionError(f"{name}.rationale must include [EST]")
    if body.get("illustrative") is not True:
        raise AssumptionError(f"{name}.illustrative must be true")
    if name in RATE_PARAMETERS and not (low >= 0 and high <= 1):
        raise AssumptionError(f"{name} low/high must stay inside [0, 1]")
    if name == "discount_rate_annual" and high >= 1:
        raise AssumptionError("discount_rate_annual high must be < 1")
    if name == "working_days_per_month" and not (low > 0 and high <= 31):
        raise AssumptionError("working_days_per_month low/high must stay in (0, 31]")
    return Parameter(
        name=name,
        value=value,
        low=low,
        high=high,
        unit=unit,
        distribution=distribution,
        rationale=rationale,
        illustrative=True,
    )


def load_case(path: Path) -> CaseFile:
    """Load a case file from disk. File reads retry with a short capped backoff."""
    raw = _read_yaml(path)
    doc = _mapping(raw, "case file")
    if doc.get("schema_version") != 1:
        raise AssumptionError("schema_version must be 1")
    meta_raw = _mapping(doc.get("case"), "case")
    case_id = _text(meta_raw.get("id"), "case.id")
    title = _text(meta_raw.get("title"), "case.title")
    company = _text(meta_raw.get("company"), "case.company")
    status = meta_raw.get("status")
    if status not in {"implemented", "design-only"}:
        raise AssumptionError("case.status must be implemented or design-only")
    if meta_raw.get("fictional") is not True:
        raise AssumptionError("case.fictional must be true")
    currency = _text(meta_raw.get("currency"), "case.currency")
    narrative = _text(meta_raw.get("narrative"), "case.narrative")
    narrative_es_raw = meta_raw.get("narrative_es")
    narrative_es = narrative if narrative_es_raw is None else _text(narrative_es_raw, "case.narrative_es")
    slot = _text(meta_raw.get("measured_cost_slot"), "case.measured_cost_slot")
    horizon = doc.get("horizon_months")
    if isinstance(horizon, bool) or not isinstance(horizon, int):
        raise AssumptionError("horizon_months must be an integer")
    parameters_raw = _mapping(doc.get("parameters"), "parameters")
    names = tuple(parameters_raw)
    if names == DAILY_PARAMETERS:
        volume_mode: Literal["daily", "monthly"] = "daily"
    elif names == MONTHLY_PARAMETERS:
        volume_mode = "monthly"
    else:
        raise AssumptionError("parameters must be the daily set or the monthly set, in order")
    parameters = {name: _parameter(name, parameters_raw[name]) for name in names}
    scenarios_raw = _mapping(doc.get("scenarios"), "scenarios")
    if set(scenarios_raw) != {"pessimistic", "base", "optimistic"}:
        raise AssumptionError("scenarios must be pessimistic, base and optimistic")
    scenarios: dict[str, dict[str, float]] = {}
    for scenario_name, overrides_raw in scenarios_raw.items():
        overrides_map = _mapping(overrides_raw, scenario_name)
        overrides: dict[str, float] = {}
        for key, value in overrides_map.items():
            if key not in parameters:
                raise AssumptionError(f"{scenario_name} overrides unknown parameter {key}")
            overrides[key] = _number(value, f"{scenario_name}.{key}")
        scenarios[scenario_name] = overrides
    meta = CaseMeta(
        case_id=case_id,
        title=title,
        company=company,
        status=status,
        fictional=True,
        currency=currency,
        narrative=narrative,
        narrative_es=narrative_es,
        horizon_months=horizon,
        measured_cost_slot=slot,
    )
    case = CaseFile(meta=meta, parameters=parameters, scenarios=scenarios, volume_mode=volume_mode)
    validate_assumptions(assumptions_from_case(case))
    for scenario_name in ("pessimistic", "base", "optimistic"):
        validate_assumptions(assumptions_for_scenario(case, scenario_name))
    return case


def assumptions_from_case(case: CaseFile, *, override: float | None = None) -> Assumptions:
    values = {name: spec.value for name, spec in case.parameters.items()}
    return _assumptions_from_values(case, values, override=override)


def assumptions_for_scenario(case: CaseFile, scenario: str, *, override: float | None = None) -> Assumptions:
    if scenario not in case.scenarios:
        raise AssumptionError(f"unknown scenario {scenario}")
    values = {name: spec.value for name, spec in case.parameters.items()}
    values.update(case.scenarios[scenario])
    return _assumptions_from_values(case, values, override=override)


def apply_parameter(assumptions: Assumptions, name: str, value: float) -> Assumptions:
    """Return a copy with one input replaced. Does not accept the override field."""
    if (
        not hasattr(assumptions, name)
        or name.startswith("_")
        or name
        in {
            "agent_cost_per_run",
            "agent_cost_per_run_override",
            "currency",
            "case_id",
            "horizon_months",
        }
    ):
        raise AssumptionError(f"cannot vary {name}")
    updated = Assumptions(
        volume_per_day=assumptions.volume_per_day,
        volume_per_month=assumptions.volume_per_month,
        working_days_per_month=assumptions.working_days_per_month,
        manual_minutes_per_item=assumptions.manual_minutes_per_item,
        loaded_cost_per_hour=assumptions.loaded_cost_per_hour,
        manual_error_rate=assumptions.manual_error_rate,
        agent_error_rate=assumptions.agent_error_rate,
        cost_of_error=assumptions.cost_of_error,
        input_tokens=assumptions.input_tokens,
        output_tokens=assumptions.output_tokens,
        input_price_per_million=assumptions.input_price_per_million,
        output_price_per_million=assumptions.output_price_per_million,
        agent_cost_per_run_override=assumptions.agent_cost_per_run_override,
        review_minutes=assumptions.review_minutes,
        review_rate=assumptions.review_rate,
        implementation_cost=assumptions.implementation_cost,
        monthly_run_cost=assumptions.monthly_run_cost,
        adoption_ramp_months=assumptions.adoption_ramp_months,
        discount_rate_annual=assumptions.discount_rate_annual,
        horizon_months=assumptions.horizon_months,
        currency=assumptions.currency,
        case_id=assumptions.case_id,
    )
    object.__setattr__(updated, name, value)
    validate_assumptions(updated)
    return updated


def scale_volume(assumptions: Assumptions, factor: float) -> Assumptions:
    if factor < 0:
        raise AssumptionError("volume factor must be >= 0")
    if assumptions.volume_per_month is not None:
        return apply_parameter(assumptions, "volume_per_month", assumptions.volume_per_month * factor)
    assert assumptions.volume_per_day is not None
    return apply_parameter(assumptions, "volume_per_day", assumptions.volume_per_day * factor)


def apply_measured_cost(assumptions: Assumptions, path: Path) -> Assumptions:
    """Replace tokens x price with a measured per-run cost.

    The file must say ``status: measured``. A stub is refused so placeholder
    numbers cannot leak into a result.
    """
    raw = _read_yaml(path)
    doc = _mapping(raw, "measured cost")
    if doc.get("kind") == "eval_run_bill" or "runs" in doc:
        raise AssumptionError(
            "eval-run bill is not a per-item override; the /23 conversion is [EST] and is not applied"
        )
    if doc.get("status") != "measured":
        raise AssumptionError("measured cost file is applied only when status is measured")
    value = _number(doc.get("agent_cost_per_run"), "agent_cost_per_run")
    _text(doc.get("source"), "source")
    updated = _clone(assumptions, agent_cost_per_run_override=value)
    validate_assumptions(updated)
    return updated


def _assumptions_from_values(case: CaseFile, values: dict[str, float], *, override: float | None) -> Assumptions:
    def take(name: str) -> float:
        return values[name]

    daily = case.volume_mode == "daily"
    return Assumptions(
        volume_per_day=take("volume_per_day") if daily else None,
        volume_per_month=None if daily else take("volume_per_month"),
        working_days_per_month=take("working_days_per_month") if daily else 0.0,
        manual_minutes_per_item=take("manual_minutes_per_item"),
        loaded_cost_per_hour=take("loaded_cost_per_hour"),
        manual_error_rate=take("manual_error_rate"),
        agent_error_rate=take("agent_error_rate"),
        cost_of_error=take("cost_of_error"),
        input_tokens=take("input_tokens"),
        output_tokens=take("output_tokens"),
        input_price_per_million=take("input_price_per_million"),
        output_price_per_million=take("output_price_per_million"),
        agent_cost_per_run_override=override,
        review_minutes=take("review_minutes"),
        review_rate=take("review_rate"),
        implementation_cost=take("implementation_cost"),
        monthly_run_cost=take("monthly_run_cost"),
        adoption_ramp_months=take("adoption_ramp_months"),
        discount_rate_annual=take("discount_rate_annual"),
        horizon_months=case.meta.horizon_months,
        currency=case.meta.currency,
        case_id=case.meta.case_id,
    )


def _clone(assumptions: Assumptions, **changes: float | None) -> Assumptions:
    data = {
        "volume_per_day": assumptions.volume_per_day,
        "volume_per_month": assumptions.volume_per_month,
        "working_days_per_month": assumptions.working_days_per_month,
        "manual_minutes_per_item": assumptions.manual_minutes_per_item,
        "loaded_cost_per_hour": assumptions.loaded_cost_per_hour,
        "manual_error_rate": assumptions.manual_error_rate,
        "agent_error_rate": assumptions.agent_error_rate,
        "cost_of_error": assumptions.cost_of_error,
        "input_tokens": assumptions.input_tokens,
        "output_tokens": assumptions.output_tokens,
        "input_price_per_million": assumptions.input_price_per_million,
        "output_price_per_million": assumptions.output_price_per_million,
        "agent_cost_per_run_override": assumptions.agent_cost_per_run_override,
        "review_minutes": assumptions.review_minutes,
        "review_rate": assumptions.review_rate,
        "implementation_cost": assumptions.implementation_cost,
        "monthly_run_cost": assumptions.monthly_run_cost,
        "adoption_ramp_months": assumptions.adoption_ramp_months,
        "discount_rate_annual": assumptions.discount_rate_annual,
        "horizon_months": assumptions.horizon_months,
        "currency": assumptions.currency,
        "case_id": assumptions.case_id,
    }
    data.update(changes)
    return Assumptions(**data)  # type: ignore[arg-type]
