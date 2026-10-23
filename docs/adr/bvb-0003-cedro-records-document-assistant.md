# ADR 0003: Build vs buy — Document assistant for internal policy binders

- Status: proposed (fictional worked example, illustrative [EST] inputs)
- Date: 2026-10-17
- Tool: roi_and_build_vs_buy 0.2.1
- Organisation: Cedro Records (fictional)
- Case: `examples/cedro_records`

## Decision

On the weighted criteria, prefer **Build in-house** (`build`) with score 4.3600.

This ADR records the matrix result and the cash result side by side. A person accepts, rejects, or revises it. The tool does not buy, provision, or contact a vendor.

## Options considered

| Option | Id | Weighted score | 3-year operating USD | 3-year USD with exit |
| --- | --- | ---: | ---: | ---: |
| Build in-house | `build` | 4.3600 | 80751.76 | 80751.76 |
| Vendor A - Folio Cloud | `vendor_a` | 3.4200 | 107428.39 | 127428.39 |
| Vendor B - Parchment Lane | `vendor_b` | 2.3800 | 54776.98 | 99776.98 |

Operating totals exclude exit. The with-exit column adds exit cost in the last year. Every score and every dollar figure in the source YAML is illustrative and marked [EST]. Dollar figures are simulated.

## Criteria

Scores run from 1 to 5. A higher score is better for the buyer, including on cost and risk. Weights sum to 1.

| Criterion | Weight |
| --- | ---: |
| Control | 0.16 |
| Time to value | 0.08 |
| 3-year TCO | 0.12 |
| Vendor risk | 0.14 |
| Security and compliance | 0.24 |
| Maintainability | 0.10 |
| Extensibility | 0.08 |
| Exit cost | 0.08 |

### Rationales for the leading option

- **Control** (5/5) [EST], illustrative: Indexes and passage logs would stay on storage the cooperative already operates, under the team's own access rules.
- **Time to value** (2/5) [EST], illustrative: Indexing the binders and reviewing citations takes longer than switching on a hosted search box.
- **3-year TCO** (4/5) [EST], illustrative: The build is a small retrieval service. After year one the modeled cash is maintenance, review, and a modest run cost.
- **Vendor risk** (5/5) [EST], illustrative: No vendor can reprice the archive or change the data-use terms. Continuity depends on the internal maintainer.
- **Security and compliance** (5/5) [EST], illustrative: Policy text does not leave the fictional tenancy. The team still has to log queries and honor retention.
- **Maintainability** (3/5) [EST], illustrative: One maintainer can own the index job and the eval set. Absence of that person is the main operational risk.
- **Extensibility** (4/5) [EST], illustrative: New collections can be added as folders in the same pipeline, without a vendor schema change.
- **Exit cost** (5/5) [EST], illustrative: The index and the eval questions remain with the cooperative. There is no modeled contract exit fee.

## Cash picture (base scenario)

- Against `vendor_a`: Build operating cost becomes lower than or equal to Vendor A - Folio Cloud in year 2.
- Against `vendor_a` including exit: Build cost including exit becomes lower than or equal to Vendor A - Folio Cloud in year 2.
- Against `vendor_b`: Build operating cost stays above Vendor B - Parchment Lane in every year of the horizon. There is no build crossover on operating cost.
- Against `vendor_b` including exit: Build cost including exit becomes lower than or equal to Vendor B - Parchment Lane in year 3.

Lowest 3-year operating total in the base scenario: **Vendor B - Parchment Lane** (`vendor_b`) at 54776.98 USD, simulated.

## What would have to change to flip the decision

- If **Time to value** weight increases by 0.295 (new weight 0.375) and the other weights scale proportionally, the winner becomes `vendor_a`.
- If **Maintainability** weight increases by 0.437 (new weight 0.537) and the other weights scale proportionally, the winner becomes `vendor_a`.
- A criterion missing from this list stays put inside the searched band.

Winner stability under ±0.05 and ±0.10 one-at-a-time shifts: 100.00% of feasible scenarios. Full rank stability: 100.00%.

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
python -m roi_and_build_vs_buy decide report --case examples/cedro_records --out out/report.md --adr-id 0003 --adr-out out/adr.md
```

Cost of that command: 0 USD. It does not call a model or a vendor API.
