"""Three-year total cost of ownership for one build option and one or more buy options.

Cash rules, all in the case currency (USD in the worked examples):

- Build year 1 includes initial engineering, infra, model run cost, eval/ops hours,
  and review hours. Later years replace initial engineering with maintenance, which
  is `maintenance_pct_of_initial_build` times the initial engineering cost.
- Run volume compounds with `volume_growth_per_year`. Infra and people hours stay flat.
- Buy year 1 includes integration. License and usage compound with the annual
  price-increase assumption. Exit cost is excluded from operating totals and added
  once, in the last year, on the with-exit total.
- Amounts that are currency are rounded to cents at each component.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.build_vs_buy.prices import validate_tree
from roi_and_build_vs_buy.build_vs_buy.quantities import MONEY_UNIT, Quantity, parse_decimal, parse_quantity
from roi_and_build_vs_buy.build_vs_buy.yaml_io import load_mapping

_CENT = Decimal("0.01")
_MAX_HORIZON = 10


@dataclass(frozen=True)
class Tier:
    """One usage band. `up_to_runs` is null on the open-ended last band."""

    up_to_runs: int | None
    price_per_run: Quantity


@dataclass(frozen=True)
class BuildSpec:
    """Build-side drivers."""

    engineering_hours: Quantity
    engineering_rate_per_hour: Quantity
    infra_per_year: Quantity
    runs_per_year: Quantity
    tokens_per_run: Quantity
    cost_per_1k_tokens: Quantity
    maintenance_pct_of_initial_build: Quantity
    eval_ops_hours_per_year: Quantity
    review_hours_per_year: Quantity


@dataclass(frozen=True)
class BuySpec:
    """One vendor offer."""

    option_id: str
    label: str
    vendor: str
    seats: Quantity
    license_per_seat_per_year: Quantity
    integration_hours: Quantity
    integration_rate_per_hour: Quantity
    exit_cost: Quantity
    annual_price_increase: Quantity
    usage_tiers: tuple[Tier, ...]


@dataclass(frozen=True)
class Scenario:
    """A named shock applied on top of the base drivers."""

    scenario_id: str
    label: str
    engineering_hours_multiplier: Decimal
    runs_multiplier: Decimal
    annual_price_increase_override: Decimal | None


@dataclass(frozen=True)
class TcoInput:
    """A fully validated TCO case."""

    case_id: str
    org: str
    title: str
    as_of: str
    currency: str
    horizon_years: int
    fictional: bool
    simulated: bool
    volume_growth_per_year: Quantity
    build: BuildSpec
    buy_options: tuple[BuySpec, ...]
    scenarios: tuple[Scenario, ...]


@dataclass(frozen=True)
class YearSpend:
    """Spend in one year and the cumulative total through that year."""

    year: int
    components: dict[str, Decimal]
    spend: Decimal
    cumulative: Decimal


@dataclass(frozen=True)
class OptionProjection:
    """Year-by-year cash for one option."""

    option_id: str
    label: str
    years: tuple[YearSpend, ...]
    operating_total: Decimal
    exit_cost: Decimal
    total_with_exit: Decimal


@dataclass(frozen=True)
class BreakEven:
    """First year in which build cumulative operating cost is <= the buy option."""

    buy_option_id: str
    operating_crossover_year: int | None
    with_exit_crossover_year: int | None
    operating_note: str
    with_exit_note: str


@dataclass(frozen=True)
class TcoProjection:
    """Curves for every option under one scenario."""

    scenario_id: str
    scenario_label: str
    options: tuple[OptionProjection, ...]
    break_evens: tuple[BreakEven, ...]

    def option(self, option_id: str) -> OptionProjection:
        for item in self.options:
            if item.option_id == option_id:
                return item
        raise KeyError(option_id)


def load_tco(path: Path) -> TcoInput:
    """Load a TCO YAML file and reject unsourced or real-looking prices."""

    raw = load_mapping(path)
    validate_tree(raw, path.name)
    return _parse_tco(raw, path.name)


def project(model: TcoInput, scenario_id: str = "base") -> TcoProjection:
    """Project one named scenario from the YAML file."""

    scenario = _scenario_by_id(model, scenario_id)
    return _project_scenario(model, scenario)


def project_all(model: TcoInput) -> tuple[TcoProjection, ...]:
    """Project every scenario in file order."""

    return tuple(_project_scenario(model, scenario) for scenario in model.scenarios)


def project_custom(
    model: TcoInput,
    *,
    scenario_id: str,
    scenario_label: str,
    engineering_hours_multiplier: Decimal,
    runs_multiplier: Decimal,
    annual_price_increase_override: Decimal | None,
) -> TcoProjection:
    """Project a synthetic scenario. Used by monotonicity probes."""

    scenario = Scenario(
        scenario_id=scenario_id,
        label=scenario_label,
        engineering_hours_multiplier=engineering_hours_multiplier,
        runs_multiplier=runs_multiplier,
        annual_price_increase_override=annual_price_increase_override,
    )
    return _project_scenario(model, scenario)


def probe_monotonicity(model: TcoInput) -> list[str]:
    """Return human-readable failures when cost moves the wrong way.

    More runs, more build hours, and a higher price-increase assumption must
    not lower the affected operating total. Year cumulatives must not fall.
    """

    failures: list[str] = []
    base = project(model, "base")
    more_runs = project_custom(
        model,
        scenario_id="probe_runs",
        scenario_label="runs x2",
        engineering_hours_multiplier=Decimal(1),
        runs_multiplier=Decimal(2),
        annual_price_increase_override=None,
    )
    more_hours = project_custom(
        model,
        scenario_id="probe_hours",
        scenario_label="engineering hours x2",
        engineering_hours_multiplier=Decimal(2),
        runs_multiplier=Decimal(1),
        annual_price_increase_override=None,
    )
    shocked = project_custom(
        model,
        scenario_id="probe_price",
        scenario_label="price increase +0.10",
        engineering_hours_multiplier=Decimal(1),
        runs_multiplier=Decimal(1),
        annual_price_increase_override=_max_increase_plus(model, Decimal("0.10")),
    )
    for option in base.options:
        other = more_runs.option(option.option_id)
        if other.operating_total < option.operating_total:
            failures.append(f"monotonicity: doubling runs lowered {option.option_id} operating total")
        hours = more_hours.option(option.option_id)
        price = shocked.option(option.option_id)
        if option.option_id == "build":
            if hours.operating_total < option.operating_total:
                failures.append("monotonicity: doubling engineering hours lowered build cost")
            if price.operating_total != option.operating_total:
                failures.append("monotonicity: price increase changed build operating total")
        else:
            if hours.operating_total != option.operating_total:
                failures.append(f"monotonicity: engineering hours changed buy option {option.option_id}")
            if price.operating_total < option.operating_total:
                failures.append(f"monotonicity: a higher price increase lowered {option.option_id}")
        previous = Decimal(0)
        for year in option.years:
            if year.cumulative < previous:
                failures.append(f"monotonicity: {option.option_id} cumulative fell in year {year.year}")
            if year.spend < 0:
                failures.append(f"monotonicity: {option.option_id} spend is negative")
            previous = year.cumulative
    return failures


def usage_cost(tiers: tuple[Tier, ...], runs: Decimal) -> Decimal:
    """Price `runs` across ordered usage tiers."""

    if runs < 0:
        raise ValidationError(["runs must be >= 0"])
    if not tiers:
        raise ValidationError(["usage_tiers must be non-empty"])
    if any(tier.up_to_runs is None for tier in tiers[:-1]):
        raise ValidationError(["only the last usage tier may omit up_to_runs"])
    if tiers[-1].up_to_runs is not None and Decimal(tiers[-1].up_to_runs) < runs:
        raise ValidationError(["usage tiers do not cover the run volume"])
    remaining = runs
    lower = Decimal(0)
    cost = Decimal(0)
    for tier in tiers:
        if tier.up_to_runs is None:
            band = remaining
            lower_next = lower
        else:
            upper = Decimal(tier.up_to_runs)
            if upper < lower:
                raise ValidationError(["usage tiers must be in ascending order"])
            band = min(remaining, upper - lower)
            lower_next = upper
        if band < 0:
            band = Decimal(0)
        cost += band * tier.price_per_run.value
        remaining -= band
        lower = lower_next
        if remaining <= 0:
            break
    if remaining > 0:
        raise ValidationError(["usage tiers do not cover the run volume"])
    return cost


def _project_scenario(model: TcoInput, scenario: Scenario) -> TcoProjection:
    build = _project_build(model, scenario)
    buy = tuple(_project_buy(model, spec, scenario) for spec in model.buy_options)
    options = (build, *buy)
    breaks = tuple(_break_even(build, item) for item in buy)
    return TcoProjection(
        scenario_id=scenario.scenario_id,
        scenario_label=scenario.label,
        options=options,
        break_evens=breaks,
    )


def _project_build(model: TcoInput, scenario: Scenario) -> OptionProjection:
    hours = model.build.engineering_hours.value * scenario.engineering_hours_multiplier
    rate = model.build.engineering_rate_per_hour.value
    initial = _money(hours * rate)
    people = _money((model.build.eval_ops_hours_per_year.value + model.build.review_hours_per_year.value) * rate)
    infra = _money(model.build.infra_per_year.value)
    maintenance_base = _money(initial * model.build.maintenance_pct_of_initial_build.value)
    years: list[YearSpend] = []
    cumulative = Decimal(0)
    for year in range(1, model.horizon_years + 1):
        runs = _runs_in_year(model, scenario, year)
        run_cost = _money(_run_cost(model.build, runs))
        engineering = initial if year == 1 else Decimal(0)
        maintenance = Decimal(0) if year == 1 else maintenance_base
        components = {
            "engineering": engineering,
            "maintenance": maintenance,
            "infra": infra,
            "run_cost": run_cost,
            "eval_and_review": people,
        }
        spend = _money(sum(components.values(), Decimal(0)))
        cumulative = _money(cumulative + spend)
        years.append(YearSpend(year=year, components=components, spend=spend, cumulative=cumulative))
    return OptionProjection(
        option_id="build",
        label="Build",
        years=tuple(years),
        operating_total=cumulative,
        exit_cost=Decimal(0),
        total_with_exit=cumulative,
    )


def _project_buy(model: TcoInput, spec: BuySpec, scenario: Scenario) -> OptionProjection:
    increase = (
        scenario.annual_price_increase_override
        if scenario.annual_price_increase_override is not None
        else spec.annual_price_increase.value
    )
    integration = _money(spec.integration_hours.value * spec.integration_rate_per_hour.value)
    exit_cost = _money(spec.exit_cost.value)
    years: list[YearSpend] = []
    cumulative = Decimal(0)
    for year in range(1, model.horizon_years + 1):
        factor = (Decimal(1) + increase) ** (year - 1)
        runs = _runs_in_year(model, scenario, year)
        license = _money(spec.seats.value * spec.license_per_seat_per_year.value * factor)
        usage = _money(usage_cost(spec.usage_tiers, runs) * factor)
        integration_year = integration if year == 1 else Decimal(0)
        components = {
            "integration": integration_year,
            "license": license,
            "usage": usage,
        }
        spend = _money(sum(components.values(), Decimal(0)))
        cumulative = _money(cumulative + spend)
        years.append(YearSpend(year=year, components=components, spend=spend, cumulative=cumulative))
    with_exit_years = _add_exit(years, exit_cost)
    return OptionProjection(
        option_id=spec.option_id,
        label=spec.label,
        years=with_exit_years,
        operating_total=cumulative,
        exit_cost=exit_cost,
        total_with_exit=with_exit_years[-1].cumulative,
    )


def _add_exit(years: list[YearSpend], exit_cost: Decimal) -> tuple[YearSpend, ...]:
    """Return a copy of the curve whose last year includes the exit cost.

    Operating components stay on the original objects only through year H-1.
    The last year gains an `exit` component. Callers that need operating
    cumulatives use `operating_total`, which is computed before this copy.
    """

    copied: list[YearSpend] = []
    running = Decimal(0)
    for index, year in enumerate(years):
        components = dict(year.components)
        spend = year.spend
        if index == len(years) - 1:
            components["exit"] = exit_cost
            spend = _money(spend + exit_cost)
        running = _money(running + spend)
        copied.append(YearSpend(year=year.year, components=components, spend=spend, cumulative=running))
    return tuple(copied)


def _runs_in_year(model: TcoInput, scenario: Scenario, year: int) -> Decimal:
    growth = model.volume_growth_per_year.value
    return model.build.runs_per_year.value * scenario.runs_multiplier * ((Decimal(1) + growth) ** (year - 1))


def _run_cost(build: BuildSpec, runs: Decimal) -> Decimal:
    return runs * build.tokens_per_run.value / Decimal(1000) * build.cost_per_1k_tokens.value


def _break_even(build: OptionProjection, buy: OptionProjection) -> BreakEven:
    operating_year = _first_year_build_leads(build.years, buy.years, use_operating_buy=True)
    with_exit_year = _first_year_build_leads(build.years, buy.years, use_operating_buy=False)
    return BreakEven(
        buy_option_id=buy.option_id,
        operating_crossover_year=operating_year,
        with_exit_crossover_year=with_exit_year,
        operating_note=_crossover_note(buy.label, operating_year, "operating cost"),
        with_exit_note=_crossover_note(buy.label, with_exit_year, "cost including exit"),
    )


def _first_year_build_leads(
    build_years: tuple[YearSpend, ...],
    buy_years: tuple[YearSpend, ...],
    *,
    use_operating_buy: bool,
) -> int | None:
    """Year where build cumulative first drops to or below the buy cumulative.

    For the operating comparison the buy curve's last year includes exit in
    `buy.years`, so operating cumulative is reconstructed as cumulative minus
    the exit component.
    """

    for build_year, buy_year in zip(build_years, buy_years, strict=True):
        buy_cumulative = buy_year.cumulative
        if use_operating_buy:
            buy_cumulative = buy_cumulative - buy_year.components.get("exit", Decimal(0))
        if build_year.cumulative <= buy_cumulative:
            return build_year.year
    return None


def _crossover_note(label: str, year: int | None, kind: str) -> str:
    if year is None:
        return f"Build {kind} stays above {label} in every year of the horizon. There is no build crossover on {kind}."
    if year == 1:
        return f"Build {kind} is lower than {label} from year 1."
    return f"Build {kind} becomes lower than or equal to {label} in year {year}."


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _max_increase_plus(model: TcoInput, delta: Decimal) -> Decimal:
    highest = max(spec.annual_price_increase.value for spec in model.buy_options)
    return highest + delta


def _scenario_by_id(model: TcoInput, scenario_id: str) -> Scenario:
    for scenario in model.scenarios:
        if scenario.scenario_id == scenario_id:
            return scenario
    raise ValidationError([f"unknown scenario {scenario_id}"])


def _parse_tco(raw: dict[str, object], path: str) -> TcoInput:
    case_id = _text(raw, "case_id", path)
    org = _text(raw, "org", path)
    title = _text(raw, "title", path)
    as_of = _text(raw, "as_of", path)
    currency = _text(raw, "currency", path)
    if currency != MONEY_UNIT:
        raise ValidationError([f"{path} currency must be {MONEY_UNIT} in this version"])
    if raw.get("fictional") is not True:
        raise ValidationError([f"{path} must set fictional: true"])
    if raw.get("simulated") is not True:
        raise ValidationError([f"{path} must set simulated: true"])
    horizon = raw.get("horizon_years")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or not 1 <= horizon <= _MAX_HORIZON:
        raise ValidationError([f"{path} horizon_years must be an integer from 1 to {_MAX_HORIZON}"])
    assumptions = raw.get("assumptions")
    if not isinstance(assumptions, dict):
        raise ValidationError([f"{path} assumptions must be a mapping"])
    growth = parse_quantity(assumptions.get("volume_growth_per_year"), f"{path}.assumptions.volume_growth_per_year")
    _require_unit(growth, "fraction", f"{path}.assumptions.volume_growth_per_year")
    _require_fraction(growth, f"{path}.assumptions.volume_growth_per_year")
    build_node = raw.get("build")
    if not isinstance(build_node, dict):
        raise ValidationError([f"{path} build must be a mapping"])
    build = _parse_build(build_node, path)
    buy_node = raw.get("buy_options")
    if not isinstance(buy_node, list) or not buy_node:
        raise ValidationError([f"{path} buy_options must be a non-empty list"])
    buy_options = tuple(_parse_buy(item, f"{path}.buy_options[{i}]") for i, item in enumerate(buy_node))
    seen = {item.option_id for item in buy_options}
    if len(seen) != len(buy_options):
        raise ValidationError([f"{path} has duplicate buy option ids"])
    if "build" in seen:
        raise ValidationError([f"{path} buy option id 'build' is reserved"])
    scenarios = _parse_scenarios(raw.get("scenarios"), path)
    if not any(item.scenario_id == "base" for item in scenarios):
        raise ValidationError([f"{path} scenarios must include id base"])
    return TcoInput(
        case_id=case_id,
        org=org,
        title=title,
        as_of=as_of,
        currency=currency,
        horizon_years=horizon,
        fictional=True,
        simulated=True,
        volume_growth_per_year=growth,
        build=build,
        buy_options=buy_options,
        scenarios=scenarios,
    )


def _parse_build(node: dict[object, object], path: str) -> BuildSpec:
    def q(name: str) -> Quantity:
        return parse_quantity(node.get(name), f"{path}.build.{name}")

    spec = BuildSpec(
        engineering_hours=q("engineering_hours"),
        engineering_rate_per_hour=q("engineering_rate_per_hour"),
        infra_per_year=q("infra_per_year"),
        runs_per_year=q("runs_per_year"),
        tokens_per_run=q("tokens_per_run"),
        cost_per_1k_tokens=q("cost_per_1k_tokens"),
        maintenance_pct_of_initial_build=q("maintenance_pct_of_initial_build"),
        eval_ops_hours_per_year=q("eval_ops_hours_per_year"),
        review_hours_per_year=q("review_hours_per_year"),
    )
    _require_unit(spec.engineering_rate_per_hour, MONEY_UNIT, f"{path}.build.engineering_rate_per_hour")
    _require_unit(spec.infra_per_year, MONEY_UNIT, f"{path}.build.infra_per_year")
    _require_unit(spec.cost_per_1k_tokens, MONEY_UNIT, f"{path}.build.cost_per_1k_tokens")
    _require_unit(spec.maintenance_pct_of_initial_build, "fraction", f"{path}.build.maintenance_pct")
    _require_fraction(spec.maintenance_pct_of_initial_build, f"{path}.build.maintenance_pct")
    return spec


def _parse_buy(node: object, path: str) -> BuySpec:
    if not isinstance(node, dict):
        raise ValidationError([f"{path} must be a mapping"])

    def q(name: str) -> Quantity:
        return parse_quantity(node.get(name), f"{path}.{name}")

    option_id = node.get("id")
    label = node.get("label")
    vendor = node.get("vendor")
    if not isinstance(option_id, str) or not option_id.strip():
        raise ValidationError([f"{path}.id must be a non-empty string"])
    if not isinstance(label, str) or not label.strip():
        raise ValidationError([f"{path}.label must be a non-empty string"])
    if not isinstance(vendor, str) or not vendor.strip():
        raise ValidationError([f"{path}.vendor must be a non-empty string"])
    tiers_node = node.get("usage_tiers")
    if not isinstance(tiers_node, list) or not tiers_node:
        raise ValidationError([f"{path}.usage_tiers must be a non-empty list"])
    tiers: list[Tier] = []
    for index, tier in enumerate(tiers_node):
        if not isinstance(tier, dict):
            raise ValidationError([f"{path}.usage_tiers[{index}] must be a mapping"])
        cap = tier.get("up_to_runs")
        if cap is not None and (isinstance(cap, bool) or not isinstance(cap, int)):
            raise ValidationError([f"{path}.usage_tiers[{index}].up_to_runs must be an integer or null"])
        price = parse_quantity(tier.get("price_per_run"), f"{path}.usage_tiers[{index}].price_per_run")
        _require_unit(price, MONEY_UNIT, f"{path}.usage_tiers[{index}].price_per_run")
        tiers.append(Tier(up_to_runs=cap, price_per_run=price))
    spec = BuySpec(
        option_id=option_id.strip(),
        label=label.strip(),
        vendor=vendor.strip(),
        seats=q("seats"),
        license_per_seat_per_year=q("license_per_seat_per_year"),
        integration_hours=q("integration_hours"),
        integration_rate_per_hour=q("integration_rate_per_hour"),
        exit_cost=q("exit_cost"),
        annual_price_increase=q("annual_price_increase"),
        usage_tiers=tuple(tiers),
    )
    _require_unit(spec.license_per_seat_per_year, MONEY_UNIT, f"{path}.license_per_seat_per_year")
    _require_unit(spec.integration_rate_per_hour, MONEY_UNIT, f"{path}.integration_rate_per_hour")
    _require_unit(spec.exit_cost, MONEY_UNIT, f"{path}.exit_cost")
    _require_unit(spec.annual_price_increase, "fraction", f"{path}.annual_price_increase")
    _require_fraction(spec.annual_price_increase, f"{path}.annual_price_increase")
    return spec


def _parse_scenarios(node: object, path: str) -> tuple[Scenario, ...]:
    if not isinstance(node, list) or not node:
        raise ValidationError([f"{path} scenarios must be a non-empty list"])
    parsed: list[Scenario] = []
    seen: set[str] = set()
    for index, item in enumerate(node):
        if not isinstance(item, dict):
            raise ValidationError([f"{path}.scenarios[{index}] must be a mapping"])
        scenario_id = item.get("id")
        label = item.get("label")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            raise ValidationError([f"{path}.scenarios[{index}].id must be a string"])
        if not isinstance(label, str) or not label.strip():
            raise ValidationError([f"{path}.scenarios[{index}].label must be a string"])
        if scenario_id in seen:
            raise ValidationError([f"duplicate scenario id {scenario_id}"])
        seen.add(scenario_id)
        override_raw = item.get("annual_price_increase_override")
        override = (
            None
            if override_raw is None
            else parse_decimal(override_raw, f"{path}.scenarios[{index}].annual_price_increase_override")
        )
        if override is not None and (override < 0 or override > 1):
            raise ValidationError([f"{path}.scenarios[{index}] price override must be a fraction from 0 to 1"])
        parsed.append(
            Scenario(
                scenario_id=scenario_id.strip(),
                label=label.strip(),
                engineering_hours_multiplier=parse_decimal(
                    item.get("engineering_hours_multiplier", "1"),
                    f"{path}.scenarios[{index}].engineering_hours_multiplier",
                ),
                runs_multiplier=parse_decimal(
                    item.get("runs_multiplier", "1"),
                    f"{path}.scenarios[{index}].runs_multiplier",
                ),
                annual_price_increase_override=override,
            )
        )
    return tuple(parsed)


def _require_unit(quantity: Quantity, unit: str, path: str) -> None:
    if quantity.unit != unit:
        raise ValidationError([f"{path} unit must be {unit}"])


def _require_fraction(quantity: Quantity, path: str) -> None:
    if quantity.value < 0 or quantity.value > 1:
        raise ValidationError([f"{path} must be between 0 and 1"])


def _text(node: dict[str, object], key: str, path: str) -> str:
    value = node.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError([f"{path} {key} must be a non-empty string"])
    return value.strip()
