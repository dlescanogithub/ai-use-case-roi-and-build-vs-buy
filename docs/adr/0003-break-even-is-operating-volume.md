# ADR 0003 — Break-even is operating volume

- Status: accepted
- Date: 2026-10-17

## Context

"Break-even" sometimes means the month payback hits zero, and sometimes the volume where the month stops losing money.

## Decision

Break-even volume is the steady-state monthly item count where net monthly savings are zero: fixed run cost / quality-adjusted savings per item, when that savings figure is positive.

It does not include implementation cost. Payback carries the implementation cost.

If unit savings are not positive and fixed cost is positive, break-even volume is none, with a reason string. The model does not return a negative volume.

## Consequences

A case can pay back slowly and still have a low operating break-even, or the reverse. Readers have to look at both numbers. The one-pagers print both.
