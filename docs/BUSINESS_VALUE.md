# Value plan: `ai-use-case-roi-and-build-vs-buy`

> **Important notice**
>
> - **Fictional organisations.** Puerto Gris Parcel Co., Bruma Freight, and Cedro Records are invented in this repo. They are not clients and they are not employers. The weekly-report case is a personal sketch. Source: [BUSINESS_CASE.md](BUSINESS_CASE.md) and the `fictional: true` flag on each case file.
> - **No second set of volumes.** This file does not add a [SYN] customer, a [SYN] call volume, or a [SYN] dollar figure. Every quantity below is already in [BUSINESS_CASE.md](BUSINESS_CASE.md), [COST.md](COST.md), [METRICS.md](METRICS.md), the assumption YAML, or a committed result file. Where this file repeats a number, it keeps that source's rounding. Full precision for the ROI cases is in `docs/results/refund_desk.json` and `docs/results/weekly_report.json`.
> - **Labels used here**
>   - **MEASURED**: this repo records a command, a date, and a result.
>   - **[EST]**: an illustrative input. The YAML rationale contains `[EST]`.
>   - **SIMULATED**: the program's arithmetic on those [EST] inputs. Not a saving a company achieved.
>   - **UNVERIFIED**: something this repo does not check (a certification, a shadow month, a real desk).
> - **[SYN]** is not used. Inventing a parallel baseline would contradict the case files.
> - Package `roi_and_build_vs_buy` 0.2.0. Distribution name `ai-use-case-roi-and-build-vs-buy`.
> - The 2026-10-17 result files name git `6d55a15`. Pytest, both eval gates, both forced regressions, the secret scan, and mypy were run again on 2026-10-22 on tree `6452c09` (Python 3.12.3). That run is recorded in [METRICS.md](METRICS.md). It did not re-time `publish-docs` or the decision-report latency sample, and it did not change the case YAML.

---

## 1. Buyer and problem

The buyer this repo is written for is a person preparing a pilot conversation. They bring the YAML, not a slide with one number. Finance would own the discount rate and any real price. The process owner would own minutes, error cost, review rate, seats, and exit. Nobody in this repository is that person for a real company. Source: [BUSINESS_CASE.md](BUSINESS_CASE.md), "Who would use it".

The problem, from the case files:

- A build-versus-buy slide hides two questions that can disagree: which option scores highest once control, risk, and exit are weighted, and which option is cheaper over three years. On the committed Bruma Freight inputs the weighted winner is `build` (score 3.7000) and the lowest 3-year operating total is `vendor_b`. Source: [BUSINESS_CASE.md](BUSINESS_CASE.md).
- A token price hides a third question: after review time, residual errors, a fixed monthly cost, and a slow ramp, does the sketch pay back. On the refund-desk file the pessimistic scenario never pays back. Source: the same document and `docs/results/refund_desk.json`.

The tool does not approve a purchase, a refund, a vendor, or a rollout. Decision ADRs stay `proposed`.

## 2. Value levers

These are the levers the code actually computes. They are not a claim that any of them has been observed on a live desk.

| Lever | What moves it | Where |
| --- | --- | --- |
| Quality-adjusted savings per item | Manual minutes and the loaded hourly cost, minus reviewer time, minus residual errors, minus the illustrative token cost | [ADR 0002](adr/0002-quality-adjusted-savings.md), `src/roi_and_build_vs_buy/roi/model.py` |
| Net monthly savings | Steady volume times that per-item figure, minus `monthly_run_cost` charged in full from month 1 | Same ADR. The ramp scales volume, not the fixed cost |
| Payback and 3-year NPV | Implementation cost at month 0, the monthly cash flows, and the annual discount rate converted to a monthly rate | `model.py`. Payback may be `never`. Search window: 360 months |
| Break-even volume | Fixed monthly cost divided by per-item savings, when savings are positive. Implementation cost is not in this volume | [ADR 0003](adr/0003-break-even-is-operating-volume.md) |
| Weighted winner versus cheapest cash | Eight weights that sum to 1, scores 1–5, and a separate 3-year TCO. Exit cost is outside the operating total and is added in the last year | `docs/examples/bruma-freight-report.md` |
| Winner stability | One weight at a time, shifted by 0.05 or 0.10, infeasible shifts dropped, the rest rescaled to sum to 1 | Same report. 19 of 28 feasible shifts on Bruma keep `build` |

The point of the kit is the disagreement, not a single recommendation. A cheap operating total can still lose on control, risk, and exit. A high score can still fail payback. Source: [BUSINESS_CASE.md](BUSINESS_CASE.md).

## 3. Baseline versus the figure in the repo

"Baseline" here means the manual or pre-choice state encoded as [EST] inputs. "Figure in the repo" is either MEASURED software output or SIMULATED arithmetic. There is no committed business target beyond that arithmetic. [METRICS.md](METRICS.md) says a green test suite is not a successful rollout.

| KPI | Baseline | Figure in the repo | Label | Later measurement (not done here) |
| --- | --- | --- | --- | --- |
| Refund desk, minutes per item | 12 minutes [EST], loaded cost USD 32 per hour [EST] | Review on the base file is 5 minutes on a 0.50 share of items [EST]. The model does not publish a measured minute | [EST] inputs. SIMULATED outputs below | Time sampling on a real desk. UNVERIFIED |
| Refund desk, manual error share | 0.06 [EST], USD 25 per error [EST] | Residual agent error rate 0.02 [EST]. Residual error cost per item in the result file is the model's product | [EST], then SIMULATED | A labeled sample. UNVERIFIED. No model is called |
| Refund desk, steady net monthly savings | The manual process is the baseline the [EST] minutes describe. This repo does not record a measured monthly saving | USD 12,775.15 base; USD -1,700.00 pessimistic; USD 31,982.79 optimistic | SIMULATED | Absolute error versus a shadow month. UNVERIFIED. [METRICS.md](METRICS.md) |
| Refund desk, payback | Not measured | 17.08 months base; never on the pessimistic set; 3.85 months optimistic | SIMULATED | Same. Payback is not implementation divided by the steady month. [DISCOVERY.md](DISCOVERY.md) |
| Refund desk, 3-year NPV | Not measured | USD 180,923.12 base; USD -350,556.83 pessimistic; USD 874,596.57 optimistic. Discount rate 0.10 [EST] | SIMULATED | Not measured |
| Refund desk, break-even volume | Not measured | 412.43 items per month on the base file. Operating volume only | SIMULATED | Not measured |
| Refund desk, Monte Carlo NPV (2,000 draws, seed 42) | Ranges are the low and high in the YAML [EST] | P10 USD -5,178.08, P50 USD 167,292.34, P90 USD 380,101.33 | SIMULATED | Not a confidence interval from field data. [RISKS.md](RISKS.md) |
| Weekly report, net monthly / payback / NPV | Four reports a month and a 90 minute write are [EST]. Every draft is still reviewed (`review_rate` 1) [EST] | Base USD 168.96, payback 1.78 months, NPV USD 5,114.00. Pessimistic NPV USD -2,469.59 and it never pays back | SIMULATED | Not measured. The pessimistic story is a cheap hour and a long review |
| Bruma Freight, weighted score | No client score exists | `build` 3.7000, `vendor_a` 3.6200, `vendor_b` 3.0200 | [EST] scores, calculated weighted total | Replace the scores. UNVERIFIED until then |
| Bruma Freight, winner stability | Not a field rate | 67.86% (19 of 28 feasible shifts). Cedro Records is 100.00% (28 of 28) on the same grid shape | Calculated from [EST] weights. Confirmed again by the eval gate on 2026-10-22 | Not a probability that building is right |
| Bruma Freight, 3-year operating cash | Not a quote | `build` USD 129,433.40, `vendor_b` USD 72,117.33, gap USD 57,316.07 with `vendor_b` lower. Including exit, the same pair differs by USD 2,683.93 the other way (`vendor_b` with exit USD 132,117.33) | SIMULATED from [EST] | A renewal or a real rate sheet. UNVERIFIED |
| Bruma Freight, smallest flip | Not measured | Raising the time-to-value weight by 0.031 (from 0.20 to 0.231) makes `vendor_a` the winner | Calculated from [EST] | [DISCOVERY.md](DISCOVERY.md) question 3 |
| Cedro Records, same shape | Not a client | Weighted winner `build` at 4.3600. Lowest operating total is `vendor_b` (USD 54,776.98 operating, USD 99,776.98 with exit). `build` operating USD 80,751.76 | SIMULATED from [EST] | Same caveat |
| Both eval gates | No assistant is scored | Exit 0, printed `BOTH EVAL GATES PASSED` | MEASURED 2026-10-17 and again 2026-10-22 | The gate checks the calculator, not an assistant |
| Forced regressions | A green regression would mean the gate went blind | ROI regression exit 1 (savings identity and break-even). Decision regression exit 1 (`golden_winner: expected build got vendor_b`, stability 59.09 below 67.86) | MEASURED 2026-10-17 and again 2026-10-22 | The 59.09% line is the calculator on weights edited on purpose |
| Unit tests and coverage | CI floor is 80% (`pyproject.toml`) | 80 passed, pytest-cov total coverage 90.98% | MEASURED 2026-10-22. Same counts were recorded on 2026-10-17 | [METRICS.md](METRICS.md) |
| Default path cost | n/a | USD 0. No tokens sent on `publish-docs` or `decide report` | MEASURED 2026-10-17 for the timed commands. The 2026-10-22 eval run also had a cost cap of 0 | [COST.md](COST.md) |
| Share of case inputs replaced by a measurement | 0. The 23-case eval bill is recorded beside the files and was not written into them | 0 | MEASURED as a count of replacements, stated in [METRICS.md](METRICS.md) | [REPLACE_THE_ASSUMPTIONS.md](REPLACE_THE_ASSUMPTIONS.md) |

Refund-desk unit figures on the base file, SIMULATED, from the README result table and `docs/results/refund_desk.json`: cost per completed item with review USD 1.34, quality-adjusted savings per item USD 6.06, residual error cost per item USD 0.50, illustrative agent cost per run USD 0.0051.

Largest one-at-a-time NPV swings on that file: `volume_per_day`, `manual_minutes_per_item`, `loaded_cost_per_hour`.

## 4. ROI model

The model is monthly, pure Python, and the YAML file is the only numeric source for a case. Definitions, copied from [ADR 0002](adr/0002-quality-adjusted-savings.md) and the module docstring in `src/roi_and_build_vs_buy/roi/model.py`:

- Manual cost per item = labor + expected cost of manual errors.
- Labor = `manual_minutes_per_item / 60 * loaded_cost_per_hour`.
- Agent run cost = input tokens / 1e6 × input price + output tokens / 1e6 × output price, unless a measured-cost file overrides it. The override path refuses the 23-case eval bill.
- Review cost = `review_rate * review_minutes / 60 * loaded_cost_per_hour`.
- Cost per completed item = agent run cost + review cost.
- Residual error cost = `agent_error_rate * cost_of_error`.
- Quality-adjusted savings per item = manual cost − cost per completed item − residual error cost.
- Net monthly savings in steady state = monthly volume × quality-adjusted savings − fixed monthly run cost.
- Adoption is linear up to 1 across `adoption_ramp_months`, then flat. The fixed cost does not shrink during the ramp.
- NPV discounts the monthly cash flows over the horizon (36 months in both sample files). Implementation sits at month 0.
- Break-even volume is the steady-state monthly volume where net monthly savings are zero. It excludes implementation.
- Payback searches up to 360 months and is explicit when the case never pays back.

This file does not publish a single ROI percentage of the form (benefit − cost) / cost. The published results are payback, break-even volume, and NPV. A one-year quotient would be a new number, and it would disagree with the 17.08 month payback, which already includes the ramp.

### [EST] assumptions, refund desk (base)

Source: `assumptions/refund_desk.yaml` and the input table in [ONE_PAGER_EN.md](ONE_PAGER_EN.md). Every row is `illustrative: true`.

| Input | Base value |
| --- | --- |
| volume_per_day | 120 items/day |
| working_days_per_month | 21 |
| manual_minutes_per_item | 12 |
| loaded_cost_per_hour | USD 32 |
| manual_error_rate | 0.06 |
| agent_error_rate | 0.02 |
| cost_of_error | USD 25 |
| input_tokens / output_tokens | 1800 / 400 |
| input price / output price | USD 1.5 / USD 6 per million tokens |
| review_minutes / review_rate | 5 minutes / 0.50 |
| implementation_cost | USD 180,000 |
| monthly_run_cost | USD 2,500 |
| adoption_ramp_months | 6 |
| discount_rate_annual | 0.10 |
| horizon | 36 months |

Pessimistic overrides in the same file, still [EST]: volume 70 per day, 8 manual minutes, review rate 0.85, agent error rate 0.05, implementation USD 280,000, ramp 12 months, monthly run cost USD 5,000. That set never pays back (SIMULATED NPV USD -350,556.83).

Optimistic overrides, still [EST]: volume 170 per day, 16 manual minutes, review rate 0.20, agent error rate 0.008, implementation USD 90,000, ramp 3 months, monthly run cost USD 1,200. SIMULATED NPV USD 874,596.57, payback 3.85 months.

### [EST] assumptions, weekly report (base)

Source: `assumptions/weekly_report.yaml`. Personal sketch. The hourly rate is an assumption about the reader's own time. It is not a wage and not an employer figure.

| Input | Base value |
| --- | --- |
| volume_per_month | 4 |
| manual_minutes_per_item | 90 |
| loaded_cost_per_hour | USD 40 |
| review_minutes / review_rate | 20 minutes / 1 |
| implementation_cost | USD 300 |
| monthly_run_cost | USD 20 |
| adoption_ramp_months | 1 |
| discount_rate_annual | 0.08 |

The pessimistic personal case lowers the hourly assumption and lengthens the review. It never pays back. Source: [BUSINESS_CASE.md](BUSINESS_CASE.md).

### What would have to be true

For the Bruma sketch, someone would need to believe the illustrative scores and the exit dollars, knowing that a 0.031 move in one weight flips the winner. For the refund sketch to be even worth a pilot conversation, someone would need to believe the [EST] volume, the minutes, and a review rate that does not climb to the pessimistic 0.85. Those beliefs are not checked here. Source: [BUSINESS_CASE.md](BUSINESS_CASE.md), "What would have to be true".

## 5. Cost table

Two costs. Do not mix them. Running the repository is MEASURED at USD 0 on the default path. The dollars inside a worked example are [EST] and SIMULATED. Source: [COST.md](COST.md).

### Running the tools (MEASURED)

| Scenario | Provider | Tokens | Cost | Timing | Date |
| --- | --- | --- | --- | --- | --- |
| Publish both ROI sample cases, 2,000 Monte Carlo draws, seed 42 | none (template provider, local CPU) | 0 sent | USD 0 | 0.751 seconds for the whole command. One sample, so p50 and p95 are not a distribution | 2026-10-17, Python 3.12.3, package 0.2.0. Command in [COST.md](COST.md). Not re-timed on 2026-10-22 |
| `decide report` on Bruma Freight | none | 0 | 0 USD | p50 0.152 s, p95 0.158 s, 30 sequential runs, percentile index `round(p/100*(n-1))` | 2026-10-17. Not re-timed on 2026-10-22 |
| Both eval gates | cassette plus template, no network | 0 | USD 0 (caps are 0) | not separately timed | Exit 0 on 2026-10-17 and again on 2026-10-22 |

### Inside the worked examples ([EST], SIMULATED)

| Scenario | Tokens or units | Cost | Price date |
| --- | --- | --- | --- |
| Refund desk, illustrative agent run | 1800 input + 400 output [EST] | USD 0.0051 per item, from [EST] prices of USD 1.5 and USD 6 per million | [EST] 2026-10-17, `assumptions/refund_desk.yaml`. Not a measured bill and not a list price |
| Weekly report, illustrative agent run | 8000 input + 2500 output [EST] | USD 0.027 per item, simulated | [EST] 2026-10-17, `assumptions/weekly_report.yaml` |
| Bruma Freight build, year-1 model run cost | 24,000 runs × 2,500 tokens [EST] | 0.01 USD per run (240.00 USD in year 1) | [EST] 2026-10-17, `examples/bruma_freight/tco.yaml` |
| Bruma Freight Vendor A license (Harborline Desk) | 12 seats [EST] | 4,200 USD per seat per year, simulated, before the 8% increase assumption | same file |
| Bruma Freight Vendor B license (Quayloop) | 12 seats [EST] | 1,500 USD per seat per year, simulated, before the 12% increase assumption | same file |
| Cedro Records build, year-1 model run cost | 8,000 runs × 4,000 tokens [EST] | 0.008 USD per run (64.00 USD in year 1) at 0.002 USD / 1k tokens | [EST] 2026-10-17, `examples/cedro_records/tco.yaml` |

Latency and quality of those agent runs are not measured. This repo does not call a model on the default path.

### A measured bill that is not a case input (MEASURED, not applied)

| Sample | Billed USD | Tokens | Source |
| --- | --- | --- | --- |
| 23-case eval run, non-reasoning | US$0.036–0.037 for the whole run | about 66–70k input / 3–3.4k output | xAI, recorded from `agent-runtime-evals` commit `c1efdfd`, 2026-10-17. Not a per-refund cost |
| 23-case eval run, grok-4.3 | US$0.072 for the whole run | 62.7k input / 14.5k output, including about 11.6k reasoning | same commit |

List prices were read the same day from `https://docs.x.ai/docs/models` (short context, under 200k prompt tokens: US$1.25 input and US$2.50 output per million for grok-4.3 and for grok-4.20-0309-non-reasoning). Those list prices times the token counts do not equal the billed totals, so the measured figure is the bill. Record: `assumptions/measured_eval_run_cost.yaml`.

[EST] conversion, not applied: `per_production_item_usd = billed_eval_run_usd / 23`. The dollars and the 23 are measured. The equality is not. The one-pager prints the split as US$0.001565 to US$0.001609 per case for the non-reasoning range, and US$0.003130 per case for grok-4.3, display rounded to 6 decimal places. Those quotients are [EST] and are not the NPV.

`ROI_ENABLE_REAL_PROVIDER` and `DECIDE_REAL_PROVIDER` default to 0. The ROI flag has no HTTP client. The decision eval ignores the real-provider flag and uses a cassette.

## 6. Measurement plan

Phase 0 is this calculator, in shadow. Phase 1 would replace [EST] inputs one field at a time and keep the old file in git. Phase 2 (a dashboard or a live effect) is not started. Source: [SCOPE.md](SCOPE.md) and [DISCOVERY.md](DISCOVERY.md).

What a later pilot would measure, and the status in this repo. Source: [METRICS.md](METRICS.md), "What success would mean on a real case, later".

| Question | Why it would matter | Status here |
| --- | --- | --- |
| Absolute error of forecast net savings versus a shadow month | Tells you if the YAML was fantasy | UNVERIFIED. No shadow month exists |
| Share of case-file inputs replaced by a measurement | Discovery completeness | 0, as stated in that doc |
| Review rate in the pilot versus the assumed rate | The pessimistic ROI case hinges on this | UNVERIFIED |
| Residual error rate on a labeled sample | Quality adjustment | UNVERIFIED. No model is called |
| Winner stability after a real score file replaces the example | Tells you if the ranking was an artifact of the illustration | UNVERIFIED. The 67.86% is the committed Bruma file |
| Time from an assumption change to a regenerated report | Operational hygiene | The publish and `decide report` commands are the mechanism. A person still has to read them. The 2026-10-17 timings are in [COST.md](COST.md) |
| Incidents where a simulated number was presented as actual savings | Governance failure | None recorded, because this repo has no audience beyond the file |

Replacement steps are in [REPLACE_THE_ASSUMPTIONS.md](REPLACE_THE_ASSUMPTIONS.md). Adapting both modules past the fictional files is described in [ADAPT_TO_A_REAL_CLIENT.md](ADAPT_TO_A_REAL_CLIENT.md). A per-item override is a different file with `status: measured` and `roi run --measured-cost`. Do not paste a price-page number and call it measured.

Software checks that stay in force on every change:

- `python3 -m pytest` with the coverage floor of 80% in `pyproject.toml`.
- Both eval gates exit 0.
- Both forced regressions exit non-zero. CI treats a zero from `make eval-regression` as a failure.
- `python3 -m roi_and_build_vs_buy.secretscan .` reports no findings.
- `python3 -m mypy` reports no issues.

## 7. Risks

Probability and impact below are the labels in [RISKS.md](RISKS.md), dated 2026-10-17. That file says they are not a measured risk study. Owners are roles.

| Risk | Label in RISKS.md | Why it matters for the value plan | Mitigation already in the repo |
| --- | --- | --- | --- |
| A guessed minute, score, or error rate is treated as fact | Probability high, impact high | The NPV and the winner both move with those inputs | Rationales must contain `[EST]`. Reports say simulated |
| Base case only, pessimistic ignored | Probability high, impact high | The refund pessimistic NPV is USD -350,556.83 and never pays back. Bruma's lead is 0.08 points | Both scenarios are in the committed output |
| Vendor lock-in understated | Medium on a close case, impact high | On Bruma, `vendor_b` wins on operating cost and loses once exit is included | Exit is its own criterion and its own cash column |
| Review cost ignored | Medium, impact high | Quality-adjusted savings subtract review and residual errors | Review minutes and review rate are required inputs |
| Illustrative token price quoted as a vendor price | Medium, impact medium | The USD 0.0051 figure is [EST] | The measured-cost slot rejects stubs and refuses the 23-case bill |
| Monte Carlo read as a field confidence interval | Medium, impact high | P10 NPV on the refund file is negative | Draws are labeled simulated. Ranges are the YAML low and high |
| Simulated dollars used as a budget | Medium, impact high | USD 180,923.12 is arithmetic, not a saving | Reports repeat simulated and [EST] |
| Formula bug that still looks consistent | Low, impact high | A wrong savings identity would still print a confident NPV | The ROI gate restates the identity. The forced regression must exit 1 |
| Secret committed | Low, impact high | A key in a doc would fail the scan | `.env` is gitignored. The scanner runs in CI |

Not covered, and not measured: legal review of automated refunds, customer harm from a wrong refund, insurance, staffing plans, and the security of a future connector. Source: the closing paragraph of [RISKS.md](RISKS.md).

## 8. MEASURED versus not

| Claim | Status |
| --- | --- |
| 80 tests passed, pytest-cov total coverage 90.98% on a clean tree, Python 3.12.3, pytest 9.1.1, coverage 7.17.0, on 2026-10-22 | MEASURED. Command in the README Proof section. The coverage table for that run shows 2,905 statements, 262 missed, and rounds the same total to 91%. pytest also printed `CoverageWarning: Module roi_and_build_vs_buy was previously imported, but not measured`. The 90.98% figure is the total the tool printed on a clean tree. A second run the same day, with `out/traces/eval.jsonl` already present, printed 91.02% (261 missed) because `trace.unlink()` then ran |
| Same 80 passed and 90.98% on 2026-10-17 | MEASURED then. That line did not record a pytest version |
| Both eval gates exit 0, Bruma stability 67.86%, Cedro stability 100.00%, on 2026-10-22 as well as 2026-10-17 | MEASURED |
| Both forced regressions exit 1, with the messages in [METRICS.md](METRICS.md) | MEASURED on both dates |
| Secret scan findings 0, mypy clean on 55 source files | MEASURED on both dates. Today's mypy is 2.4.0 |
| Publish wall time 0.751 s, decision-report p50 0.152 s and p95 0.158 s, default cost USD 0 | MEASURED 2026-10-17 only. Not re-timed on 2026-10-22 |
| 23-case xAI bills US$0.036–0.037 and US$0.072 | MEASURED in `agent-runtime-evals` commit `c1efdfd`, recorded here. Not a per-item production cost. The split by 23 is [EST] and is not applied |
| NPV, payback, break-even, TCO totals, winner stability percentages | SIMULATED or calculated from [EST] inputs. Not MEASURED business results |
| Minutes saved, review rate, residual error rate, and forecast error on a real desk | UNVERIFIED. Not in this repo |
| Security scores of 4 or 3 on the fictional vendors | [EST] case notes. UNVERIFIED as a certification. The report says so |
| Any ROI percentage of the form (benefit − cost) / cost for a year-1 budget | Not published. This file does not calculate one |

A person owns the assumption files. This repo does not own a decision.
