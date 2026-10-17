# ADR 0005 — XLSX formulas and CSV values

- Status: accepted
- Date: 2026-10-17

## Context

Someone will want to type a new volume into a spreadsheet and see NPV move. Someone else will want a diffable file in git.

## Decision

`openpyxl` writes `model.xlsx`. Output cells are formulas that reference named inputs. `results.csv` and `inputs.csv` store the Python values. CI checks that the formula cells start with `=`. CI does not evaluate them.

Spreadsheet payback is a helper column over 360 months. Python uses the same search limit. NPV in the sheet sums discounted cash flows for `horizon_months` only.

## Consequences

A reader who changes an input in Excel and a reader who changes the YAML can disagree until both are regenerated or recalculated. The CSV is the source of the numbers quoted in the docs. The XLSX is the live scratchpad.
