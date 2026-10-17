# ADR 0002: Build vs buy — Internal support agent for shipment-exception tickets

- Status: proposed (fictional worked example, illustrative [EST] inputs)
- Date: 2026-10-17
- Tool: roi_and_build_vs_buy 0.2.0
- Organisation: Bruma Freight (fictional)
- Case: `examples/bruma_freight`

## Decision

On the weighted criteria, prefer **Build in-house** (`build`) with score 3.7000.

This ADR records the matrix result and the cash result side by side. A person accepts, rejects, or revises it. The tool does not buy, provision, or contact a vendor.

## Options considered

| Option | Id | Weighted score | 3-year operating USD | 3-year USD with exit |
| --- | --- | ---: | ---: | ---: |
| Build in-house | `build` | 3.7000 | 129433.40 | 129433.40 |
| Vendor A - Harborline Desk | `vendor_a` | 3.6200 | 175259.79 | 203259.79 |
| Vendor B - Quayloop | `vendor_b` | 3.0200 | 72117.33 | 132117.33 |

Operating totals exclude exit. The with-exit column adds exit cost in the last year. Every score and every dollar figure in the source YAML is illustrative and marked [EST]. Dollar figures are simulated.

## Criteria

Scores run from 1 to 5. A higher score is better for the buyer, including on cost and risk. Weights sum to 1.

| Criterion | Weight |
| --- | ---: |
| Control | 0.10 |
| Time to value | 0.20 |
| 3-year TCO | 0.18 |
| Vendor risk | 0.12 |
| Security and compliance | 0.14 |
| Maintainability | 0.10 |
| Extensibility | 0.08 |
| Exit cost | 0.08 |

### Rationales for the leading option

- **Control** (5/5) [EST], illustrative: The team would own the prompts, the tools, and the tenancy, and could change the workflow without a vendor release.
- **Time to value** (2/5) [EST], illustrative: A careful internal first version is slower than a hosted pilot, and the desk wants a human review loop before drafts are trusted.
- **3-year TCO** (3/5) [EST], illustrative: Year-one engineering is heavy. Later years are maintenance, review, and a small run cost, so the cash picture against seats is mixed.
- **Vendor risk** (5/5) [EST], illustrative: There is no vendor who can raise the price or shut the product down. The remaining risk is hiring and continuity of the internal team.
- **Security and compliance** (4/5) [EST], illustrative: Ticket text stays in the company's own tenancy in these fictional case notes. The team still has to run access control and retention.
- **Maintainability** (3/5) [EST], illustrative: The same small team would own evals, prompts, and breakage. That is workable, and it is also easy to under-staff.
- **Extensibility** (5/5) [EST], illustrative: New ticket types and internal tools can be added in the team's own repository when the desk asks for them.
- **Exit cost** (5/5) [EST], illustrative: Stopping this approach means keeping the code and the eval set. There is no contract exit fee in the model.

## Cash picture (base scenario)

- Against `vendor_a`: Build operating cost becomes lower than or equal to Vendor A - Harborline Desk in year 2.
- Against `vendor_a` including exit: Build cost including exit becomes lower than or equal to Vendor A - Harborline Desk in year 2.
- Against `vendor_b`: Build operating cost stays above Vendor B - Quayloop in every year of the horizon. There is no build crossover on operating cost.
- Against `vendor_b` including exit: Build cost including exit becomes lower than or equal to Vendor B - Quayloop in year 3.

Lowest 3-year operating total in the base scenario: **Vendor B - Quayloop** (`vendor_b`) at 72117.33 USD, simulated.

## What would have to change to flip the decision

- If **Control** weight decreases by 0.038 (new weight 0.062) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **Time to value** weight increases by 0.031 (new weight 0.231) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **3-year TCO** weight increases by 0.061 (new weight 0.241) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **Vendor risk** weight decreases by 0.037 (new weight 0.083) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **Maintainability** weight increases by 0.067 (new weight 0.167) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **Extensibility** weight decreases by 0.039 (new weight 0.041) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **Exit cost** weight decreases by 0.039 (new weight 0.041) and the other weights scale proportionally, the winner becomes `vendor_a`.
- A criterion missing from this list stays put inside the searched band.

Winner stability under ±0.05 and ±0.10 one-at-a-time shifts: 67.86% of feasible scenarios. Full rank stability: 67.86%.

## Exit and revisit triggers

- Revisit on or before **2027-04-17** (six months after 2026-10-17).
- Revisit sooner when any of these show up in a re-run of this case:
  - The weighted winner changes.
  - Winner stability falls below 50% on the same perturbation grid.
  - A realized vendor increase exceeds the annual price-increase assumption.
  - Build engineering hours exceed the build_overrun multiplier (1.5x).
  - With-exit cash and the weighted ranking pick different options,
    and the gap is larger than the exit cost already modeled.

Exit trigger for a buy choice: a failed export drill, a price increase above the modeled assumption, or a change in the data-use terms described in the score rationales. Exit trigger for a build choice: loss of the team that owns the eval set, or a time-to-value slip that fails the revisit above.

## Consequences

- The decision record is this ADR plus the YAML inputs. Both stay in git.
- Re-running the report after an input change is the rollback. The previous ADR remains in history.
- No vendor is contacted and no budget is committed by generating this file.

## Reproduce

```bash
python -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/report.md --adr-id 0002 --adr-out out/adr.md
```

Cost of that command: 0 USD. It does not call a model or a vendor API.
