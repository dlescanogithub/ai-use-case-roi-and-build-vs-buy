"""CSV values and an XLSX workbook whose outputs are Excel formulas."""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.worksheet import Worksheet

from roi_and_build_vs_buy.roi.analysis import Analysis

EXCEL_NAMES = {
    "volume_per_day": "VolumePerDay",
    "volume_per_month": "VolumePerMonth",
    "working_days_per_month": "WorkingDays",
    "manual_minutes_per_item": "ManualMinutes",
    "loaded_cost_per_hour": "LoadedCostPerHour",
    "manual_error_rate": "ManualErrorRate",
    "agent_error_rate": "AgentErrorRate",
    "cost_of_error": "CostOfError",
    "input_tokens": "InputTokens",
    "output_tokens": "OutputTokens",
    "input_price_per_million": "InputPricePerMillion",
    "output_price_per_million": "OutputPricePerMillion",
    "review_minutes": "ReviewMinutes",
    "review_rate": "ReviewRate",
    "implementation_cost": "ImplementationCost",
    "monthly_run_cost": "MonthlyRunCost",
    "adoption_ramp_months": "AdoptionRamp",
    "discount_rate_annual": "DiscountRate",
}


def write_csv(analysis: Analysis, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    assumptions = analysis.assumptions
    result = analysis.result
    inputs_path = directory / "inputs.csv"
    with inputs_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["parameter", "value", "unit", "low", "high", "distribution", "illustrative", "rationale"])
        for spec in analysis.case.parameters.values():
            writer.writerow(
                [
                    spec.name,
                    spec.value,
                    spec.unit,
                    spec.low,
                    spec.high,
                    spec.distribution,
                    "illustrative" if spec.illustrative else "",
                    spec.rationale,
                ]
            )
    results_path = directory / "results.csv"
    with results_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value", "note"])
        rows = [
            ("currency", assumptions.currency, "[EST] inputs; simulated outputs"),
            (
                "agent_cost_per_run",
                result.unit.agent_run_cost,
                "tokens x price, or measured override",
            ),
            (
                "cost_per_completed_item",
                result.unit.cost_per_completed_item,
                "includes reviewer time",
            ),
            ("residual_error_cost", result.unit.residual_error_cost, "quality adjustment"),
            (
                "quality_adjusted_savings_per_item",
                result.unit.quality_adjusted_savings,
                "manual cost minus agent cost minus residual errors",
            ),
            ("monthly_volume_steady", result.monthly_volume_steady, "full adoption"),
            ("net_monthly_savings_steady", result.net_monthly_steady, "after fixed run cost"),
            ("break_even_volume", result.break_even_volume, result.break_even_reason),
            ("payback_status", result.payback.status, result.payback.reason),
            ("payback_months", result.payback.months, "none when the case never pays back"),
            ("npv", result.npv, "discounted over the horizon; implementation at month 0"),
            ("npv_p10", analysis.monte_carlo.npv_p10, "simulated"),
            ("npv_p50", analysis.monte_carlo.npv_p50, "simulated"),
            ("npv_p90", analysis.monte_carlo.npv_p90, "simulated"),
        ]
        for row in rows:
            writer.writerow(row)


def write_xlsx(analysis: Analysis, path: Path) -> None:
    """Workbook with live formulas. Values are also in the CSV export.

    This module does not evaluate the formulas. Excel or LibreOffice does.
    Spreadsheet payback is limited to the NPV horizon; Python searches 360 months.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    active = workbook.active
    if not isinstance(active, Worksheet):
        raise RuntimeError("workbook has no worksheet")
    inputs = active
    inputs.title = "Inputs"
    inputs.append(["key", "value", "unit", "illustrative", "rationale"])
    cells: dict[str, str] = {}
    for index, spec in enumerate(analysis.case.parameters.values(), start=2):
        inputs.cell(index, 1, spec.name)
        inputs.cell(index, 2, spec.value)
        inputs.cell(index, 3, spec.unit)
        inputs.cell(index, 4, "illustrative" if spec.illustrative else "")
        inputs.cell(index, 5, spec.rationale)
        cells[spec.name] = f"$B${index}"
    flag_row = len(analysis.case.parameters) + 3
    inputs.cell(flag_row, 1, "use_monthly_volume")
    inputs.cell(flag_row, 2, 1 if analysis.case.volume_mode == "monthly" else 0)
    inputs.cell(flag_row, 4, "illustrative")
    inputs.cell(flag_row, 5, "1 when the case is stated per month [EST]")
    _define(workbook, "UseMonthlyVolume", f"Inputs!$B${flag_row}")
    for name, excel_name in EXCEL_NAMES.items():
        if name in cells:
            _define(workbook, excel_name, f"Inputs!{cells[name]}")
        else:
            # The unused volume mode still has a name so formulas stay valid.
            blank_row = flag_row + 1
            inputs.cell(blank_row, 1, name)
            inputs.cell(blank_row, 2, 0)
            inputs.cell(blank_row, 4, "illustrative")
            inputs.cell(blank_row, 5, "unused in this volume mode")
            _define(workbook, excel_name, f"Inputs!$B${blank_row}")
            flag_row = blank_row
    inputs.cell(flag_row + 2, 1, "Illustrative numbers, replace with your own")

    model = workbook.create_sheet("Model")
    labels = [
        (
            "agent_run_cost",
            "=InputTokens/1000000*InputPricePerMillion+OutputTokens/1000000*OutputPricePerMillion",
        ),
        ("manual_labor", "=ManualMinutes/60*LoadedCostPerHour"),
        ("manual_error", "=ManualErrorRate*CostOfError"),
        ("review_cost", "=ReviewRate*(ReviewMinutes/60)*LoadedCostPerHour"),
        ("residual_error", "=AgentErrorRate*CostOfError"),
        ("quality_adjusted_savings", "=B3+B4-(B2+B5)-B6"),
        (
            "monthly_volume_steady",
            "=IF(UseMonthlyVolume=1,VolumePerMonth,VolumePerDay*WorkingDays)",
        ),
        ("net_monthly_steady", "=B8*B7-MonthlyRunCost"),
        ("break_even_volume", '=IF(B7<=0,"never",MonthlyRunCost/B7)'),
        ("monthly_discount_rate", "=(1+DiscountRate)^(1/12)-1"),
        ("npv", "=-ImplementationCost+SUM(Cashflows!E2:E361)"),
        (
            "payback_months",
            '=IF(COUNT(Cashflows!H2:H361)=0,"never",SUM(Cashflows!H2:H361))',
        ),
    ]
    model.append(["metric", "formula"])
    for offset, (label, formula) in enumerate(labels, start=2):
        model.cell(offset, 1, label)
        model.cell(offset, 2, formula)

    flows = workbook.create_sheet("Cashflows")
    flows.append(["month", "adoption", "volume", "net", "discounted", "cumulative", "blank", "payback_piece"])
    horizon = analysis.assumptions.horizon_months
    # Rows exist through the search window so a long payback still has a formula.
    # NPV sums only the horizon via a separate column marker.
    for month in range(1, 361):
        row = month + 1
        flows.cell(row, 1, f"={month}" if month == 1 else f"=A{row - 1}+1")
        flows.cell(row, 2, f"=IF(AdoptionRamp<=0,1,MIN(1,A{row}/AdoptionRamp))")
        flows.cell(row, 3, f"=Model!$B$8*B{row}")
        flows.cell(row, 4, f"=C{row}*Model!$B$7-MonthlyRunCost")
        if month <= horizon:
            flows.cell(row, 5, f"=D{row}/(1+Model!$B$11)^A{row}")
        else:
            flows.cell(row, 5, 0)
        if month == 1:
            flows.cell(row, 6, f"=-ImplementationCost+D{row}")
            flows.cell(
                row,
                8,
                f'=IF(F{row}>=0,IF(D{row}<=0,0,ImplementationCost/D{row}),"")',
            )
        else:
            flows.cell(row, 6, f"=F{row - 1}+D{row}")
            flows.cell(
                row,
                8,
                (f'=IF(AND(F{row}>=0,F{row - 1}<0),(A{row}-1)+IF(D{row}<=0,0,-F{row - 1}/D{row}),"")'),
            )
    workbook.save(path)


def _define(workbook: Workbook, name: str, attr: str) -> None:
    workbook.defined_names.add(DefinedName(name=name, attr_text=attr))
