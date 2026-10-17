# ADR 0002 — Quality-adjusted savings

- Status: accepted
- Date: 2026-10-17

## Context

"Savings" can mean labor only, or labor minus the agent, or labor minus the agent minus the errors that remain. Those are different decisions.

## Decision

- Manual cost = labor + expected cost of manual errors.
- Cost per completed item = agent run cost + reviewer time. Reviewer time is `review_rate * review_minutes / 60 * loaded cost`.
- Residual error cost = `agent_error_rate * cost_of_error`.
- Quality-adjusted savings per item = manual cost − cost per completed item − residual error cost.
- Net monthly savings = monthly volume × quality-adjusted savings − fixed monthly run cost.

The agent run cost is `input_tokens / 1e6 * input price + output_tokens / 1e6 * output price`, unless a measured-cost file overrides it.

## Consequences

A case with cheap labor and expensive residual errors can show negative savings. That is the result, not a bug. The eval gate checks this identity against the inputs, not against `unit_economics`, so a wrong formula fails closed.
