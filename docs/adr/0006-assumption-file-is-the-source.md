# ADR 0006 — The assumption file is the only numeric source

- Status: accepted
- Date: 2026-10-17

## Context

Numbers leak into README examples and then get quoted without the assumption that produced them.

## Decision

Sample numbers live in `assumptions/refund_desk.yaml` and `assumptions/weekly_report.yaml`. Docs that quote an output point at `docs/results/*.json`, the command, the date and the package version. Inputs stay illustrative [EST]. A per-item measured override is a separate file with `status: measured`. The stub in the repo is not applied. The 23-case eval bill in `assumptions/measured_eval_run_cost.yaml` is also separate: it is a measured record, and the per-item split of that bill is [EST] and is not an input.

Design-only use cases do not get a YAML of invented precision. They are named in the README and in `docs/SCOPE.md`.

## Consequences

Updating a base assumption requires regenerating the one-pagers and the JSON, and editing the README tables if the quoted cents change. That friction is intentional.
