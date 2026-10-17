# ADR 0001 — Monthly model in pure Python

- Status: accepted
- Date: 2026-10-17

## Context

The calculator has to run in CI with no native scientific stack and no network. The decision people ask for is monthly: savings, payback, a 3-year NPV.

## Decision

Cash flows are monthly. Adoption in month `t` (1-based) is `min(1, t / ramp)`, or 1 when the ramp is 0. The fixed monthly run cost is charged in full from month 1; it does not shrink during the ramp. Implementation is a cash flow at month 0. Payback searches at most 360 months and returns an explicit "never" when steady-state net savings are not positive. NumPy is not a dependency. Monte Carlo uses `random.Random`.

## Consequences

Intra-month timing is invisible. A ramp that is not linear will need a different function. Excel and Python share the 360-month window for payback. NPV uses only `horizon_months` (36 in the sample files).
