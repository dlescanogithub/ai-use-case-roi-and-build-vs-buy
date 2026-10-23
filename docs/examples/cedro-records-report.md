# Build vs buy report — Document assistant for internal policy binders

Tool: roi_and_build_vs_buy 0.2.1
As of: 2026-10-17
Organisation: Cedro Records (fictional)
Illustrative inputs, replace with your own.
Status of this case: implemented worked example. Inputs are synthetic.
Every score and every currency figure below is **[EST]** and illustrative. Currency figures are also **simulated**.
This command writes a file. It does not call a model, a vendor, or the network.

## Weighted ranking

A higher score is better on every criterion, including 3-year TCO, vendor risk, and exit cost.

| Rank | Option | Id | Control | Time to value | 3-year TCO | Vendor risk | Security and compliance | Maintainability | Extensibility | Exit cost | Total |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Build in-house | `build` | 5 [EST] | 2 [EST] | 4 [EST] | 5 [EST] | 5 [EST] | 3 [EST] | 4 [EST] | 5 [EST] | 4.3600 |
| 2 | Vendor A - Folio Cloud | `vendor_a` | 3 [EST] | 4 [EST] | 3 [EST] | 3 [EST] | 4 [EST] | 4 [EST] | 3 [EST] | 3 [EST] | 3.4200 |
| 3 | Vendor B - Parchment Lane | `vendor_b` | 2 [EST] | 5 [EST] | 3 [EST] | 2 [EST] | 2 [EST] | 3 [EST] | 2 [EST] | 1 [EST] | 2.3800 |

## Why each cell has that score

### Build in-house (`build`)

- **Control** (5 [EST]/5): Indexes and passage logs would stay on storage the cooperative already operates, under the team's own access rules.
- **Time to value** (2 [EST]/5): Indexing the binders and reviewing citations takes longer than switching on a hosted search box.
- **3-year TCO** (4 [EST]/5): The build is a small retrieval service. After year one the modeled cash is maintenance, review, and a modest run cost.
- **Vendor risk** (5 [EST]/5): No vendor can reprice the archive or change the data-use terms. Continuity depends on the internal maintainer.
- **Security and compliance** (5 [EST]/5): Policy text does not leave the fictional tenancy. The team still has to log queries and honor retention.
- **Maintainability** (3 [EST]/5): One maintainer can own the index job and the eval set. Absence of that person is the main operational risk.
- **Extensibility** (4 [EST]/5): New collections can be added as folders in the same pipeline, without a vendor schema change.
- **Exit cost** (5 [EST]/5): The index and the eval questions remain with the cooperative. There is no modeled contract exit fee.

### Vendor A - Folio Cloud (`vendor_a`)

- **Control** (3 [EST]/5): Folio Cloud offers admin roles and an export of citations in these fictional case notes. Ranking and retention still follow the product.
- **Time to value** (4 [EST]/5): A hosted workspace can be pointed at a sample binder within a short pilot, which matters less here than custody.
- **3-year TCO** (3 [EST]/5): Seat licenses for the reading room dominate. Usage is small. Integration of the binder export is the year-one project.
- **Vendor risk** (3 [EST]/5): These fictional case notes model a 6 percent annual increase and a renewal. That is manageable and still a dependency.
- **Security and compliance** (4 [EST]/5): These fictional case notes claim an audit log, a regional tenancy option, and no training on customer files. The score records the claim.
- **Maintainability** (4 [EST]/5): The vendor operates the index. The cooperative still owns which binders are in scope and how citations are checked.
- **Extensibility** (3 [EST]/5): New collections fit the product while they look like documents. A custom records system needs an integration.
- **Exit cost** (3 [EST]/5): Citations can be exported in these fictional case notes. Rebuilding the index later is a real project, with a modeled exit fee.

### Vendor B - Parchment Lane (`vendor_b`)

- **Control** (2 [EST]/5): Parchment Lane keeps ranking and retention settings inside a proprietary console, with few export switches.
- **Time to value** (5 [EST]/5): It is the fastest fictional way to get a search box in front of the reading room.
- **3-year TCO** (3 [EST]/5): Seats are cheaper than Folio Cloud. The modeled exit fee is high, and the price-increase assumption is steeper.
- **Vendor risk** (2 [EST]/5): A 15 percent increase assumption and a thin export path put the archive on a single vendor's terms.
- **Security and compliance** (2 [EST]/5): These fictional case notes say uploaded binders may be used to improve the shared service. That fails the cooperative's custody bar.
- **Maintainability** (3 [EST]/5): Day-to-day operation is light. A change in the product becomes a ticket to the vendor, not a local fix.
- **Extensibility** (2 [EST]/5): Collections outside the vendor's document model wait on their roadmap.
- **Exit cost** (1 [EST]/5): The modeled exit fee is large and these fictional case notes give no usable bulk export of the index or the feedback labels.

## Sensitivity

Rank stability (full order unchanged): **100.00%**. Winner stability: **100.00%**.

Winner stability is 28 of 28 feasible shifts on this grid, shown as a percentage rounded to two decimals. It is the share of those shifts that keep the same first-place option. It is not a probability that the decision is right, and it is not a field result. The scores and weights underneath it are illustrative [EST].

Grid: shift one weight by -0.10, -0.05, +0.05, or +0.10, then rescale the others so they still sum to 1. Feasible scenarios: 28. A weight must stay inside 0.01 and 0.90.

| Criterion | Delta | Winner | Winner held | Full rank held |
| --- | ---: | --- | --- | --- |
| Control | -0.10 | `build` | yes | yes |
| Control | -0.05 | `build` | yes | yes |
| Control | 0.05 | `build` | yes | yes |
| Control | 0.10 | `build` | yes | yes |
| Time to value | -0.05 | `build` | yes | yes |
| Time to value | 0.05 | `build` | yes | yes |
| Time to value | 0.10 | `build` | yes | yes |
| 3-year TCO | -0.10 | `build` | yes | yes |
| 3-year TCO | -0.05 | `build` | yes | yes |
| 3-year TCO | 0.05 | `build` | yes | yes |
| 3-year TCO | 0.10 | `build` | yes | yes |
| Vendor risk | -0.10 | `build` | yes | yes |
| Vendor risk | -0.05 | `build` | yes | yes |
| Vendor risk | 0.05 | `build` | yes | yes |
| Vendor risk | 0.10 | `build` | yes | yes |
| Security and compliance | -0.10 | `build` | yes | yes |
| Security and compliance | -0.05 | `build` | yes | yes |
| Security and compliance | 0.05 | `build` | yes | yes |
| Security and compliance | 0.10 | `build` | yes | yes |
| Maintainability | -0.05 | `build` | yes | yes |
| Maintainability | 0.05 | `build` | yes | yes |
| Maintainability | 0.10 | `build` | yes | yes |
| Extensibility | -0.05 | `build` | yes | yes |
| Extensibility | 0.05 | `build` | yes | yes |
| Extensibility | 0.10 | `build` | yes | yes |
| Exit cost | -0.05 | `build` | yes | yes |
| Exit cost | 0.05 | `build` | yes | yes |
| Exit cost | 0.10 | `build` | yes | yes |

### What would have to change to flip the decision

- Time to value increase by 0.295 (new weight 0.375) flips the winner to `vendor_a`.
- Maintainability increase by 0.437 (new weight 0.537) flips the winner to `vendor_a`.
A criterion missing from this list stays put inside the searched band.

## Base cash curves

### Scenario `base` — Base

USD, simulated, [EST].

#### Build (`build`)

| Year | engineering | maintenance | infra | run_cost | eval_and_review | Spend | Cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 31500.00 | 0 | 2400.00 | 64.00 | 10800.00 | 44764.00 | 44764.00 |
| 2 | 0 | 4725.00 | 2400.00 | 67.20 | 10800.00 | 17992.20 | 62756.20 |
| 3 | 0 | 4725.00 | 2400.00 | 70.56 | 10800.00 | 17995.56 | 80751.76 |

Operating total 80751.76 USD. Exit 0 USD. With exit 80751.76 USD. Simulated.

#### Vendor A - Folio Cloud (`vendor_a`)

| Year | integration | license | usage | exit | Spend | Cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 14400.00 | 28800.00 | 400.00 | 0 | 43600.00 | 43600.00 |
| 2 | 0 | 30528.00 | 445.20 | 0 | 30973.20 | 74573.20 |
| 3 | 0 | 32359.68 | 495.51 | 20000.00 | 52855.19 | 127428.39 |

Operating total 107428.39 USD. Exit 20000.00 USD. With exit 127428.39 USD. Simulated.

#### Vendor B - Parchment Lane (`vendor_b`)

| Year | integration | license | usage | exit | Spend | Cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3600.00 | 14400.00 | 320.00 | 0 | 18320.00 | 18320.00 |
| 2 | 0 | 16560.00 | 386.40 | 0 | 16946.40 | 35266.40 |
| 3 | 0 | 19044.00 | 466.58 | 45000.00 | 64510.58 | 99776.98 |

Operating total 54776.98 USD. Exit 45000.00 USD. With exit 99776.98 USD. Simulated.

Break-even against build:

- `vendor_a` operating: Build operating cost becomes lower than or equal to Vendor A - Folio Cloud in year 2.
- `vendor_a` with exit: Build cost including exit becomes lower than or equal to Vendor A - Folio Cloud in year 2.
- `vendor_b` operating: Build operating cost stays above Vendor B - Parchment Lane in every year of the horizon. There is no build crossover on operating cost.
- `vendor_b` with exit: Build cost including exit becomes lower than or equal to Vendor B - Parchment Lane in year 3.

## Where the matrix and the cash model meet

Weighted winner: `build`. Lowest base-scenario operating total: `vendor_b` at 54776.98 USD, simulated.

On this case the weighted winner and the lowest operating total are different options. The matrix is carrying control, risk, compliance, and exit, which the cash total does not. The decision owner has to say which of those stories they are buying.

### Operating totals by option

| Option | Operating USD | With exit USD |
| --- | ---: | ---: |
| Build in-house | 80751.76 | 80751.76 |
| Vendor A - Folio Cloud | 107428.39 | 127428.39 |
| Vendor B - Parchment Lane | 54776.98 | 99776.98 |

## Scenarios

- `base` (Base): lowest operating total is `vendor_b` at 54776.98 USD, simulated [EST].
- `build_overrun` (Build hours x1.5): lowest operating total is `vendor_b` at 54776.98 USD, simulated [EST].
- `price_shock` (Buy price increase 20 percent): lowest operating total is `vendor_b` at 57247.23 USD, simulated [EST].
- `volume_spike` (Run volume x2): lowest operating total is `vendor_b` at 55949.96 USD, simulated [EST].

## Provenance

Every driver in the TCO file is an envelope with `source`, `date`, and `estimate`. The loader rejects a bare number and rejects a USD figure marked `estimate: false` when the source has no https URL.

| Driver | Value | Unit | Estimate | Date | Source |
| --- | ---: | --- | --- | --- | --- |
| `assumptions.volume_growth_per_year` | 0.05 | fraction | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.engineering_hours` | 350 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.engineering_rate_per_hour` | 90 | USD | [EST] illustrative | 2026-10-17 | fictional blended rate for this worked example |
| `build.infra_per_year` | 2400 | USD | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.runs_per_year` | 8000 | runs | [EST] illustrative | 2026-10-17 | fictional query volume for a reading room |
| `build.tokens_per_run` | 4000 | tokens | [EST] illustrative | 2026-10-17 | fictional prompt-plus-passage size for a citation answer |
| `build.cost_per_1k_tokens` | 0.002 | USD | [EST] illustrative | 2026-10-17 | fictional model price used only inside this example |
| `build.maintenance_pct_of_initial_build` | 0.15 | fraction | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.eval_ops_hours_per_year` | 80 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `build.review_hours_per_year` | 40 | hours | [EST] illustrative | 2026-10-17 | fictional time to check cited passages |
| `vendor_a.seats` | 30 | seats | [EST] illustrative | 2026-10-17 | fictional reading-room headcount for this worked example |
| `vendor_a.license_per_seat_per_year` | 960 | USD | [EST] illustrative | 2026-10-17 | fictional list price for this worked example |
| `vendor_a.integration_hours` | 160 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `vendor_a.integration_rate_per_hour` | 90 | USD | [EST] illustrative | 2026-10-17 | fictional blended rate for this worked example |
| `vendor_a.exit_cost` | 20000 | USD | [EST] illustrative | 2026-10-17 | fictional exit allowance for re-indexing exported citations |
| `vendor_a.annual_price_increase` | 0.06 | fraction | [EST] illustrative | 2026-10-17 | fictional price-increase assumption for this worked example |
| `vendor_a.usage_tiers[0].price_per_run` | 0.05 | USD | [EST] illustrative | 2026-10-17 | fictional usage price for this worked example |
| `vendor_b.seats` | 30 | seats | [EST] illustrative | 2026-10-17 | fictional reading-room headcount for this worked example |
| `vendor_b.license_per_seat_per_year` | 480 | USD | [EST] illustrative | 2026-10-17 | fictional list price for this worked example |
| `vendor_b.integration_hours` | 40 | hours | [EST] illustrative | 2026-10-17 | fictional planning assumption for this worked example |
| `vendor_b.integration_rate_per_hour` | 90 | USD | [EST] illustrative | 2026-10-17 | fictional blended rate for this worked example |
| `vendor_b.exit_cost` | 45000 | USD | [EST] illustrative | 2026-10-17 | fictional exit allowance for a missing bulk export |
| `vendor_b.annual_price_increase` | 0.15 | fraction | [EST] illustrative | 2026-10-17 | fictional price-increase assumption for this worked example |
| `vendor_b.usage_tiers[0].price_per_run` | 0.04 | USD | [EST] illustrative | 2026-10-17 | fictional usage price for this worked example |

## Reproduce

```bash
python -m roi_and_build_vs_buy decide report --case examples/cedro_records --out out/report.md
```

Cost of that command: 0 USD.
