# ADR 0004: Invariant evals and dated prices

- Status: accepted for this repository
- Date: 2026-10-17
- Tool: the repository itself, package roi_and_build_vs_buy 0.2.0

## Decision

Evals in this repo check invariants, and every money figure in a TCO file carries a source, a date, and an estimate flag. A USD amount that claims to be real (`estimate: false`) without an `https://` URL is rejected.

## Options considered

| Option | Why it lost or won |
| --- | --- |
| Lock the exact ranking numbers and a transcript of function calls | Brittle. A wording change in a rationale would fail a test that was about a decision |
| Invariants: weights sum to 1, golden winner, monotonic cash, zero eval cost, no external action | Chosen. The forced-regression fixture proves the winner check can go red |
| Allow bare numbers in YAML for speed of editing | Rejected. A bare number reads like a fact. The envelope makes the [EST] label unavoidable |

## Criteria

- A reviewer can see why a number is in the file (source, date, estimate).
- CI never needs a network call to a vendor or a model.
- A bad weight edit fails closed because of `evals/golden/decisions.json`, and CI asserts that the known-bad fixture fails.

## Exit and revisit triggers

- Revisit if a real engagement needs a quote feed. That is the moment to discuss `DECIDE_REAL_PROVIDER`, still off in CI.
- Revisit if the invariant set hides a bug the team cares about. Add an invariant. Do not replace the regression test of the decision model with a snapshot of a tool trace.
- Exit this policy if the loader starts accepting bare prices. That change should fail review.

## Consequences

- Example prices in this repo are all `estimate: true` and fictional.
- `docs/examples` and ADR 0002 / 0003 are generated and compared in `tests/test_generated_docs.py`.
- The cassette, the trace, the logs, and the secret scanner are one copy in this repository, shared by both modules. The matrix, the sensitivity search, and the TCO model live beside the monthly ROI model. See [../PROVENANCE.md](../PROVENANCE.md).
