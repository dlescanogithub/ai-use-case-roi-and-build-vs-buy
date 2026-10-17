"""Measured 23-case eval bill, kept apart from the invented case inputs.

The dollars, token counts and case count are a recorded sample.
Dividing the bill by 23 is an [EST] conversion, not a measurement of one refund.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import yaml

from roi_model.retry import retry

CASES = 23
CONVERSION_FORMULA = "per_production_item_usd = billed_eval_run_usd / 23"


class MeasuredCostError(ValueError):
    """The measured-cost record is not usable."""


@dataclass(frozen=True)
class ListPrice:
    model_id: str
    input_per_million: Decimal
    output_per_million: Decimal


@dataclass(frozen=True)
class MeasuredRun:
    run_id: str
    billed_usd_low: Decimal
    billed_usd_high: Decimal
    input_tokens_low: int
    input_tokens_high: int
    output_tokens_low: int
    output_tokens_high: int
    reasoning_tokens: int | None
    token_phrase: str
    list_price_model: str


@dataclass(frozen=True)
class MeasuredEvalSample:
    source_repo: str
    commit: str
    measured_on: str
    provider: str
    price_page: str
    price_page_fetched: str
    cases: int
    conversion_formula: str
    conversion_assumption: str
    list_price_note: str
    list_prices: tuple[ListPrice, ...]
    runs: tuple[MeasuredRun, ...]

    def price_for(self, model_id: str) -> ListPrice:
        for price in self.list_prices:
            if price.model_id == model_id:
                return price
        raise MeasuredCostError(f"no list price for {model_id}")


def default_measured_path() -> Path:
    return Path(__file__).resolve().parents[2] / "assumptions" / "measured_eval_run_cost.yaml"


def per_case_est(billed_usd: Decimal, cases: int = CASES) -> Decimal:
    """[EST] Split one eval-run bill into a per-case figure."""
    if cases <= 0:
        raise MeasuredCostError("cases must be positive")
    return billed_usd / Decimal(cases)


def list_price_usd(input_tokens: int, output_tokens: int, price: ListPrice) -> Decimal:
    """Short-context list price times token counts. This is not the bill."""
    million = Decimal(1_000_000)
    input_cost = Decimal(input_tokens) * price.input_per_million
    output_cost = Decimal(output_tokens) * price.output_per_million
    return (input_cost + output_cost) / million


def load_measured_eval_sample(path: Path | None = None) -> MeasuredEvalSample:
    source = default_measured_path() if path is None else path
    raw = _read_yaml(source)
    if not isinstance(raw, dict):
        raise MeasuredCostError("measured cost file must be a mapping")
    doc = {str(key): value for key, value in raw.items()}
    if doc.get("status") != "measured":
        raise MeasuredCostError("status must be measured")
    if doc.get("kind") != "eval_run_bill":
        raise MeasuredCostError("kind must be eval_run_bill")
    if doc.get("applies_to_case_inputs") is not False:
        raise MeasuredCostError("eval-run bill must not apply to case inputs")
    cases = doc.get("cases")
    if cases != CASES:
        raise MeasuredCostError("cases must be 23")
    conversion = _mapping(doc.get("conversion"), "conversion")
    formula = _text(conversion.get("formula"), "conversion.formula")
    if formula != CONVERSION_FORMULA:
        raise MeasuredCostError("conversion formula drifted")
    if conversion.get("status") != "[EST]":
        raise MeasuredCostError("conversion status must be [EST]")
    prices_doc = _mapping(doc.get("list_prices"), "list_prices")
    models = prices_doc.get("models")
    if not isinstance(models, list) or not models:
        raise MeasuredCostError("list_prices.models must be a list")
    prices = tuple(_price(item) for item in models)
    runs_raw = doc.get("runs")
    if not isinstance(runs_raw, list) or len(runs_raw) != 2:
        raise MeasuredCostError("runs must be the two recorded samples")
    runs = tuple(_run(item) for item in runs_raw)
    sample = MeasuredEvalSample(
        source_repo=_text(doc.get("source_repo"), "source_repo"),
        commit=_text(doc.get("commit"), "commit"),
        measured_on=_text(doc.get("measured_on"), "measured_on"),
        provider=_text(doc.get("provider"), "provider"),
        price_page=_text(doc.get("price_page"), "price_page"),
        price_page_fetched=_text(doc.get("price_page_fetched"), "price_page_fetched"),
        cases=CASES,
        conversion_formula=formula,
        conversion_assumption=_text(conversion.get("assumption"), "conversion.assumption"),
        list_price_note=_text(prices_doc.get("note"), "list_prices.note"),
        list_prices=prices,
        runs=runs,
    )
    _check_bill_is_not_the_list_price(sample)
    return sample


def render_measured_markdown(*, lang: str = "en") -> str:
    """Side note for reports. Does not change the case NPV."""
    if lang not in {"en", "es"}:
        raise ValueError("lang must be en or es")
    sample = load_measured_eval_sample()
    if lang == "es":
        intro = (
            "Dato medido, aparte de los insumos inventados. Es la factura de una "
            "corrida de evaluación de 23 casos, no el costo de un reembolso de "
            "producción. No está aplicado a la VPN de esta página."
        )
    else:
        intro = (
            "Measured data, separate from the invented inputs. These are bills for "
            "one 23-case eval run, not the cost of one production refund. "
            "They are not applied to the NPV on this page."
        )
    lines = [
        intro,
        "",
        (
            f"Source: {sample.source_repo} commit {sample.commit}, measured {sample.measured_on}, "
            f"provider {sample.provider}. Price page {sample.price_page} fetched {sample.price_page_fetched}."
        ),
        "",
        "| Sample | Billed USD | Tokens | Label |",
        "| --- | --- | --- | --- |",
    ]
    for run in sample.runs:
        billed = _billed_text(run)
        lines.append(f"| {run.run_id} | {billed} | {run.token_phrase} | measured |")
    lines.extend(
        [
            "",
            f"[EST] `{sample.conversion_formula}`",
            sample.conversion_assumption.strip(),
            "",
        ]
    )
    for run in sample.runs:
        low = per_case_est(run.billed_usd_low, sample.cases)
        high = per_case_est(run.billed_usd_high, sample.cases)
        lines.append(
            f"[EST] {run.run_id}: {_billed_text(run)} / {sample.cases} = {_money_range(low, high)} per case "
            "(display rounded to 6 decimal places)."
        )
    lines.extend(["", sample.list_price_note.strip(), ""])
    for run in sample.runs:
        price = sample.price_for(run.list_price_model)
        low = list_price_usd(run.input_tokens_low, run.output_tokens_low, price)
        high = list_price_usd(run.input_tokens_high, run.output_tokens_high, price)
        lines.append(
            f"List-price reconstruction for {run.run_id} using {price.model_id} "
            f"at US${price.input_per_million} input and US${price.output_per_million} output "
            f"per million tokens: {_exact_range(low, high)}. Billed sample: {_billed_text(run)}. "
            "The reconstruction is not the measured bill."
        )
    return "\n".join(lines)


def _billed_text(run: MeasuredRun) -> str:
    if run.billed_usd_low == run.billed_usd_high:
        return f"US${_plain(run.billed_usd_low)}"
    return f"US${_plain(run.billed_usd_low)}-{_plain(run.billed_usd_high)}"


def _money_range(low: Decimal, high: Decimal) -> str:
    shown_low = _six(low)
    shown_high = _six(high)
    if shown_low == shown_high:
        return f"US${shown_low}"
    return f"US${shown_low} to US${shown_high}"


def _six(value: Decimal) -> str:
    shown = value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    return format(shown, "f")


def _exact_range(low: Decimal, high: Decimal) -> str:
    if low == high:
        return f"US${_plain(low)}"
    return f"US${_plain(low)} to US${_plain(high)}"


def _plain(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _check_bill_is_not_the_list_price(sample: MeasuredEvalSample) -> None:
    for run in sample.runs:
        price = sample.price_for(run.list_price_model)
        low = list_price_usd(run.input_tokens_low, run.output_tokens_low, price)
        high = list_price_usd(run.input_tokens_high, run.output_tokens_high, price)
        if low == run.billed_usd_low or high == run.billed_usd_high:
            raise MeasuredCostError("list-price reconstruction must not be stored as the bill")
        if high < run.billed_usd_low or low > run.billed_usd_high:
            continue
        raise MeasuredCostError("list-price reconstruction overlaps the billed total; do not treat them as the same")


def _read_yaml(path: Path) -> object:
    def _read() -> object:
        loaded: object = yaml.safe_load(path.read_text(encoding="utf-8"))
        return loaded

    return retry(_read, max_attempts=3, base_delay=0.01, backoff_cap=0.05)


def _mapping(raw: object, ctx: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise MeasuredCostError(f"{ctx} must be a mapping")
    return {str(key): value for key, value in raw.items()}


def _text(raw: object, ctx: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise MeasuredCostError(f"{ctx} must be a non-empty string")
    return raw.strip()


def _decimal(raw: object, ctx: str) -> Decimal:
    if isinstance(raw, bool) or not isinstance(raw, str):
        raise MeasuredCostError(f"{ctx} must be a decimal string")
    try:
        value = Decimal(raw)
    except ArithmeticError as exc:
        raise MeasuredCostError(f"{ctx} is not a decimal") from exc
    if not value.is_finite():
        raise MeasuredCostError(f"{ctx} must be finite")
    return value


def _int(raw: object, ctx: str) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise MeasuredCostError(f"{ctx} must be an integer")
    return raw


def _price(raw: object) -> ListPrice:
    body = _mapping(raw, "list price")
    return ListPrice(
        model_id=_text(body.get("id"), "list price id"),
        input_per_million=_decimal(body.get("input_per_million"), "input_per_million"),
        output_per_million=_decimal(body.get("output_per_million"), "output_per_million"),
    )


def _run(raw: object) -> MeasuredRun:
    body = _mapping(raw, "run")
    low = _decimal(body.get("billed_usd_low"), "billed_usd_low")
    high = _decimal(body.get("billed_usd_high"), "billed_usd_high")
    if low <= 0 or high < low:
        raise MeasuredCostError("billed range must be positive and ordered")
    reasoning = body.get("reasoning_tokens")
    reasoning_tokens = None if reasoning is None else _int(reasoning, "reasoning_tokens")
    return MeasuredRun(
        run_id=_text(body.get("id"), "run.id"),
        billed_usd_low=low,
        billed_usd_high=high,
        input_tokens_low=_int(body.get("input_tokens_low"), "input_tokens_low"),
        input_tokens_high=_int(body.get("input_tokens_high"), "input_tokens_high"),
        output_tokens_low=_int(body.get("output_tokens_low"), "output_tokens_low"),
        output_tokens_high=_int(body.get("output_tokens_high"), "output_tokens_high"),
        reasoning_tokens=reasoning_tokens,
        token_phrase=_text(body.get("token_phrase"), "token_phrase"),
        list_price_model=_text(body.get("list_price_model"), "list_price_model"),
    )
