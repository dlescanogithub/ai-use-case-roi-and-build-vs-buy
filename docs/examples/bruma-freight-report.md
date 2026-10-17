# Build vs buy report — Internal support agent for shipment-exception tickets

Tool: roi_and_build_vs_buy 0.2.0
As of: 2026-10-17
Organisation: Bruma Freight (fictional)
Illustrative inputs, replace with your own.
Status of this case: implemented worked example. Inputs are synthetic.
Every score and every currency figure below is **[EST]** and illustrative. Currency figures are also **simulated**.
This command writes a file. It does not call a model, a vendor, or the network.

## Weighted ranking

A higher score is better on every criterion, including 3-year TCO, vendor risk, and exit cost.

| Rank | Option | Id | Control | Time to value | 3-year TCO | Vendor risk | Security and compliance | Maintainability | Extensibility | Exit cost | Total |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Build in-house | `build` | 5 [EST] | 2 [EST] | 3 [EST] | 5 [EST] | 4 [EST] | 3 [EST] | 5 [EST] | 5 [EST] | 3.7000 |
| 2 | Vendor A - Harborline Desk | `vendor_a` | 3 [EST] | 4 [EST] | 4 [EST] | 3 [EST] | 4 [EST] | 4 [EST] | 3 [EST] | 3 [EST] | 3.6200 |
| 3 | Vendor B - Quayloop | `vendor_b` | 2 [EST] | 5 [EST] | 3 [EST] | 2 [EST] | 3 [EST] | 3 [EST] | 2 [EST] | 2 [EST] | 3.0200 |

## Why each cell has that score

### Build in-house (`build`)

- **Control** (5 [EST]/5): The team would own the prompts, the tools, and the tenancy, and could change the workflow without a vendor release.
- **Time to value** (2 [EST]/5): A careful internal first version is slower than a hosted pilot, and the desk wants a human review loop before drafts are trusted.
- **3-year TCO** (3 [EST]/5): Year-one engineering is heavy. Later years are maintenance, review, and a small run cost, so the cash picture against seats is mixed.
- **Vendor risk** (5 [EST]/5): There is no vendor who can raise the price or shut the product down. The remaining risk is hiring and continuity of the internal team.
- **Security and compliance** (4 [EST]/5): Ticket text stays in the company's own tenancy in these fictional case notes. The team still has to run access control and retention.
- **Maintainability** (3 [EST]/5): The same small team would own evals, prompts, and breakage. That is workable, and it is also easy to under-staff.
- **Extensibility** (5 [EST]/5): New ticket types and internal tools can be added in the team's own repository when the desk asks for them.
- **Exit cost** (5 [EST]/5): Stopping this approach means keeping the code and the eval set. There is no contract exit fee in the model.

### Vendor A - Harborline Desk (`vendor_a`)

- **Control** (3 [EST]/5): Harborline Desk allows workflow configuration and transcript export. Core routing still follows the vendor product cycle.
- **Time to value** (4 [EST]/5): A hosted pilot can start in weeks because the channel and the agent shell already exist in the fictional product.
- **3-year TCO** (4 [EST]/5): Seat licenses dominate the modeled cash. Usage stays small at this volume, and integration is a one-time cost.
- **Vendor risk** (3 [EST]/5): These fictional case notes assume an annual renewal and an 8 percent price-increase assumption. A low assumption is an exposure.
- **Security and compliance** (4 [EST]/5): These fictional case notes claim SSO, an audit log, and a no-training clause. This score records that claim, not a certification.
- **Maintainability** (4 [EST]/5): The vendor runs the platform. The internal team still owns the review queue and the acceptance tests.
- **Extensibility** (3 [EST]/5): Extensions stay inside the vendor tool model. Unusual internal systems need their own integration project.
- **Exit cost** (3 [EST]/5): Transcripts are exportable in these fictional case notes. Rebuilding the workflow elsewhere is still a project, with a modeled exit fee.

### Vendor B - Quayloop (`vendor_b`)

- **Control** (2 [EST]/5): Quayloop is the most closed of the three options. Routing rules live in a proprietary format in these fictional case notes.
- **Time to value** (5 [EST]/5): It is the fastest fictional pilot. Little integration is required to cover one narrow ticket type.
- **3-year TCO** (3 [EST]/5): The seat price is lower, the usage price per run is higher, and the modeled exit fee is large.
- **Vendor risk** (2 [EST]/5): A single vendor, a 12 percent price-increase assumption, and a thin export path concentrate the risk.
- **Security and compliance** (3 [EST]/5): These fictional case notes say customer text may be used to improve a shared model. That is a weak fit for shipment exceptions.
- **Maintainability** (3 [EST]/5): Operations stay simple while the product matches the desk. Divergence becomes a support contract.
- **Extensibility** (2 [EST]/5): New processes wait on the vendor feature list. The desk cannot add an internal tool on its own.
- **Exit cost** (2 [EST]/5): The modeled exit fee is high and the workflow export is weak, so switching later is expensive.

## Sensitivity

Rank stability (full order unchanged): **67.86%**. Winner stability: **67.86%**.

Winner stability is 19 of 28 feasible shifts on this grid, shown as a percentage rounded to two decimals. It is the share of those shifts that keep the same first-place option. It is not a probability that the decision is right, and it is not a field result. The scores and weights underneath it are illustrative [EST].

Grid: shift one weight by -0.10, -0.05, +0.05, or +0.10, then rescale the others so they still sum to 1. Feasible scenarios: 28. A weight must stay inside 0.01 and 0.90.

| Criterion | Delta | Winner | Winner held | Full rank held |
| --- | ---: | --- | --- | --- |
| Control | -0.05 | `vendor_a` | no | no |
| Control | 0.05 | `build` | yes | yes |
| Control | 0.10 | `build` | yes | yes |
| Time to value | -0.10 | `build` | yes | yes |
| Time to value | -0.05 | `build` | yes | yes |
| Time to value | 0.05 | `vendor_a` | no | no |
| Time to value | 0.10 | `vendor_a` | no | no |
| 3-year TCO | -0.10 | `build` | yes | yes |
| 3-year TCO | -0.05 | `build` | yes | yes |
| 3-year TCO | 0.05 | `build` | yes | yes |
| 3-year TCO | 0.10 | `vendor_a` | no | no |
| Vendor risk | -0.10 | `vendor_a` | no | no |
| Vendor risk | -0.05 | `vendor_a` | no | no |
| Vendor risk | 0.05 | `build` | yes | yes |
| Vendor risk | 0.10 | `build` | yes | yes |
| Security and compliance | -0.10 | `build` | yes | yes |
| Security and compliance | -0.05 | `build` | yes | yes |
| Security and compliance | 0.05 | `build` | yes | yes |
| Security and compliance | 0.10 | `build` | yes | yes |
| Maintainability | -0.05 | `build` | yes | yes |
| Maintainability | 0.05 | `build` | yes | yes |
| Maintainability | 0.10 | `vendor_a` | no | no |
| Extensibility | -0.05 | `vendor_a` | no | no |
| Extensibility | 0.05 | `build` | yes | yes |
| Extensibility | 0.10 | `build` | yes | yes |
| Exit cost | -0.05 | `vendor_a` | no | no |
| Exit cost | 0.05 | `build` | yes | yes |
| Exit cost | 0.10 | `build` | yes | yes |

### What would have to change to flip the decision

- Control decrease by 0.038 (new weight 0.062) flips the winner to `vendor_a`.
- Time to value increase by 0.031 (new weight 0.231) flips the winner to `vendor_a`.
- 3-year TCO increase by 0.061 (new weight 0.241) flips the winner to `vendor_a`.
- Vendor risk decrease by 0.037 (new weight 0.083) flips the winner to `vendor_a`.
- Maintainability increase by 0.067 (new weight 0.167) flips the winner to `vendor_a`.
- Extensibility decrease by 0.039 (new weight 0.041) flips the winner to `vendor_a`.
- Exit cost decrease by 0.039 (new weight 0.041) flips the winner to `vendor_a`.
A criterion missing from this list stays put inside the searched band.

## Base cash curves

### Scenario `base` — Base

USD, simulated, [EST].

#### Build (`build`)

| Year | engineering | maintenance | infra | run_cost | eval_and_review | Spend | Cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 47500.00 | 0 | 3600.00 | 240.00 | 17100.00 | 68440.00 | 68440.00 |
| 2 | 0 | 9500.00 | 3600.00 | 276.00 | 17100.00 | 30476.00 | 98916.00 |
| 3 | 0 | 9500.00 | 3600.00 | 317.40 | 17100.00 | 30517.40 | 129433.40 |

Operating total 129433.40 USD. Exit 0 USD. With exit 129433.40 USD. Simulated.

#### Vendor A - Harborline Desk (`vendor_a`)

| Year | integration | license | usage | exit | Spend | Cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 9500.00 | 50400.00 | 580.00 | 0 | 60480.00 | 60480.00 |
| 2 | 0 | 54432.00 | 704.16 | 0 | 55136.16 | 115616.16 |
| 3 | 0 | 58786.56 | 857.07 | 28000.00 | 87643.63 | 203259.79 |

Operating total 175259.79 USD. Exit 28000.00 USD. With exit 203259.79 USD. Simulated.

#### Vendor B - Quayloop (`vendor_b`)

| Year | integration | license | usage | exit | Spend | Cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3800.00 | 18000.00 | 1920.00 | 0 | 23720.00 | 23720.00 |
| 2 | 0 | 20160.00 | 2472.96 | 0 | 22632.96 | 46352.96 |
| 3 | 0 | 22579.20 | 3185.17 | 60000.00 | 85764.37 | 132117.33 |

Operating total 72117.33 USD. Exit 60000.00 USD. With exit 132117.33 USD. Simulated.

Break-even against build:

- `vendor_a` operating: Build operating cost becomes lower than or equal to Vendor A - Harborline Desk in year 2.
- `vendor_a` with exit: Build cost including exit becomes lower than or equal to Vendor A - Harborline Desk in year 2.
- `vendor_b` operating: Build operating cost stays above Vendor B - Quayloop in every year of the horizon. There is no build crossover on operating cost.
- `vendor_b` with exit: Build cost including exit becomes lower than or equal to Vendor B - Quayloop in year 3.

## Where the matrix and the cash model meet

Weighted winner: `build`. Lowest base-scenario operating total: `vendor_b` at 72117.33 USD, simulated.

On this case the weighted winner and the lowest operating total are different options. The matrix is carrying control, risk, compliance, and exit, which the cash total does not. The decision owner has to say which of those stories they are buying.

### Operating totals by option

| Option | Operating USD | With exit USD |
| --- | ---: | ---: |
| Build in-house | 129433.40 | 129433.40 |
| Vendor A - Harborline Desk | 175259.79 | 203259.79 |
| Vendor B - Quayloop | 72117.33 | 132117.33 |

## Scenarios

- `base` (Base): lowest operating total is `vendor_b` at 72117.33 USD, simulated [EST].
- `build_overrun` (Build hours x1.5): lowest operating total is `vendor_b` at 72117.33 USD, simulated [EST].
- `price_shock` (Buy price increase 20 percent): lowest operating total is `vendor_b` at 77546.05 USD, simulated [EST].
- `volume_spike` (Run volume x2): lowest operating total is `vendor_b` at 79695.46 USD, simulated [EST].

## Provenance

Every driver in the TCO file is an envelope with `source`, `date`, and `estimate`. The loader rejects a bare number and rejects a USD figure marked `estimate: false` when the source has no https URL.

| Driver | Value | Unit | Estimate | Date | Source |
| --- | ---: | --- | --- | --- | --- |
| `assumptions.volume_growth_per_year` | 0.15 | fraction | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.engineering_hours` | 500 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.engineering_rate_per_hour` | 95 | USD | [EST] illustrative | 2026-10-17 | fictional blended rate for this worked example |
| `build.infra_per_year` | 3600 | USD | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.runs_per_year` | 24000 | runs | [EST] illustrative | 2026-10-17 | fictional volume for a single operations desk |
| `build.tokens_per_run` | 2500 | tokens | [EST] illustrative | 2026-10-17 | fictional prompt-plus-context size for a ticket draft |
| `build.cost_per_1k_tokens` | 0.004 | USD | [EST] illustrative | 2026-10-17 | fictional model price used only inside this example |
| `build.maintenance_pct_of_initial_build` | 0.20 | fraction | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.eval_ops_hours_per_year` | 120 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.review_hours_per_year` | 60 | hours | [EST] illustrative | 2026-10-17 | fictional human review time for drafted replies |
| `vendor_a.seats` | 12 | seats | [EST] illustrative | 2026-10-17 | fictional desk headcount for this worked example |
| `vendor_a.license_per_seat_per_year` | 4200 | USD | [EST] illustrative | 2026-10-17 | fictional list price for this worked example |
| `vendor_a.integration_hours` | 100 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `vendor_a.integration_rate_per_hour` | 95 | USD | [EST] illustrative | 2026-10-17 | fictional blended rate for this worked example |
| `vendor_a.exit_cost` | 28000 | USD | [EST] illustrative | 2026-10-17 | fictional exit allowance for workflow rebuild and export work |
| `vendor_a.annual_price_increase` | 0.08 | fraction | [EST] illustrative | 2026-10-17 | fictional price-increase assumption for this worked example |
| `vendor_a.usage_tiers[0].price_per_run` | 0.03 | USD | [EST] illustrative | 2026-10-17 | fictional usage tier for this worked example |
| `vendor_a.usage_tiers[1].price_per_run` | 0.02 | USD | [EST] illustrative | 2026-10-17 | fictional usage tier for this worked example |
| `vendor_b.seats` | 12 | seats | [EST] illustrative | 2026-10-17 | fictional desk headcount for this worked example |
| `vendor_b.license_per_seat_per_year` | 1500 | USD | [EST] illustrative | 2026-10-17 | fictional list price for this worked example |
| `vendor_b.integration_hours` | 40 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `vendor_b.integration_rate_per_hour` | 95 | USD | [EST] illustrative | 2026-10-17 | fictional blended rate for this worked example |
| `vendor_b.exit_cost` | 60000 | USD | [EST] illustrative | 2026-10-17 | fictional exit allowance for a weak export path |
| `vendor_b.annual_price_increase` | 0.12 | fraction | [EST] illustrative | 2026-10-17 | fictional price-increase assumption for this worked example |
| `vendor_b.usage_tiers[0].price_per_run` | 0.08 | USD | [EST] illustrative | 2026-10-17 | fictional usage price for this worked example |

## Reproduce

```bash
python -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/report.md
```

Cost of that command: 0 USD.
