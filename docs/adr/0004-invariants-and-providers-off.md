# ADR 0004 — Invariants, and providers off

- Status: accepted
- Date: 2026-10-17

## Context

An eval that pins the exact sequence of function calls breaks when a harmless refactor lands. An eval that calls a paid API makes CI expensive and flaky.

## Decision

The gate checks invariants: savings identity, break-even equals fixed cost over unit savings, payback status is one of `immediate` / `pays_back` / `never`, a case that cannot pay back says never, more volume does not lower net savings when unit savings are non-negative, the same seed repeats, commentary has no harmful-effect phrase, trace cost is within the cap (default 0), and trace actions stay in `{read_assumptions, compute, provider_replay, write_report}`.

The default provider is `template` (no model). `cassette` replays a file. `fake` is an in-memory stand-in. `real` refuses. `ROI_ENABLE_REAL_PROVIDER` defaults to 0. No HTTP client ships, so the flag cannot spend money.

`make eval-regression` evaluates a deliberately wrong savings figure (manual labor only) and must exit 1. CI fails if that command exits 0.

## Consequences

A bug that agrees with the duplicated identity will pass. The hand-computed unit test in `tests/test_model.py` is the second lock. The gate does not prove the Monte Carlo distributions are calibrated to the real world. They are not.
