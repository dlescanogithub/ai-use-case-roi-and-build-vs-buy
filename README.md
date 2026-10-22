Illustrative numbers, replace with your own

# AI use-case ROI and build-vs-buy

## Start here

This repo proves a local calculator: a weighted build-versus-buy score, a 3-year cash model, and a monthly ROI, with both eval gates green and both forced regressions red, and with no model call on the default path. It does not prove that a company saved the simulated NPV.
One command, cost 0 USD: `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python3 -m roi_and_build_vs_buy roi demo`
Walkthrough: [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md). Value plan: [docs/BUSINESS_VALUE.md](docs/BUSINESS_VALUE.md).

The distribution name is `ai-use-case-roi-and-build-vs-buy`. The import package is `roi_and_build_vs_buy`, version 0.2.0. The command is `python -m roi_and_build_vs_buy` with subcommands `decide` and `roi`.

Puerto Gris Parcel Co., Bruma Freight, and Cedro Records are fictional. They are not clients and they are not employers.

## Problem

A build-versus-buy slide hides two questions: which option scores highest once control, risk, and exit are weighted, and which option is cheaper over three years. A token price then hides a third question: after review time, residual errors, a fixed monthly cost, and a slow ramp, does the sketch pay back. Those answers can diverge.

**Calculated result, from illustrative inputs:** on the fictional Bruma Freight case, winner stability is **67.86%**. That is 19 of 28 feasible weight shifts keeping `build` in first place.

- Date: 2026-10-17, and the same JSON fields again on 2026-10-22
- Version: `roi_and_build_vs_buy` 0.2.0
- Python: 3.12.3
- Command: `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit`
- Output: JSON field `cases[0].winner_stability_pct` = `"67.86"`

How to read 67.86%: the tool shifts one illustrative weight at a time by 0.05 or 0.10, drops shifts that would push a weight outside 0.01–0.90, rescales the rest so they still sum to 1, and counts how often `build` stays first. 19 of those 28 shifts keep `build`. The percentage is not a probability that building is the right choice, and it is not a success rate from a live desk. Cedro Records stays at 100.00% on the same grid (28 of 28).

**Simulated ROI, published 2026-10-17, same package:** command `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_and_build_vs_buy roi publish-docs` finished in 0.751 seconds and wrote a 3-year NPV of **USD 180,923.12** for the fictional refund desk. Inputs are illustrative [EST]. The NPV is simulated. The pessimistic scenario never pays back (NPV USD -350,556.83). Full precision is in `docs/results/refund_desk.json`. That publish command was not re-timed on 2026-10-22.

Replace the inputs before you treat either figure as your decision. See [docs/REPLACE_THE_ASSUMPTIONS.md](docs/REPLACE_THE_ASSUMPTIONS.md).

## Architecture

```mermaid
flowchart TD
  decideYaml["decide YAML: weights, scores, TCO [EST]"] --> matrix["Weighted matrix"]
  decideYaml --> tco["3-year TCO"]
  matrix --> sens["Winner stability"]
  matrix --> decideReport["Decision report and ADR"]
  tco --> decideReport
  sens --> decideReport
  decideReport --> human["Person picks an option to cost"]
  roiYaml["ROI YAML [EST]"] --> model["Monthly ROI model"]
  human --> roiYaml
  model --> roiOut["NPV, payback, break-even"]
  model --> tornado["Tornado, scenarios, Monte Carlo"]
  roiOut --> pages["One-pagers and phased rollout notes"]
  tornado --> pages
  gate["Both eval gates"] --> matrix
  gate --> model
```

`decide` scores a case. `roi` turns an assumption file into a monthly result. They share the `[EST]` tag, the logger, retries, the trace, and the secret scanner. They do not share one YAML schema. Detail: [docs/architecture.md](docs/architecture.md).

The default path does not call a model, a vendor, or the network. Cost to run that path: 0 USD.

## Quickstart

```bash
python3 -m pip install -e ".[dev]"
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python3 -m roi_and_build_vs_buy roi demo
python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma-freight-report.md
```

`make demo` runs the ROI demo and the Bruma Freight report. If `make` is missing, the commands above are enough. Cost of the demo is zero. No API key.

The longer check (lint, types, tests, both gates, both forced regressions) is in [How to reproduce](#how-to-reproduce).

## Business case

On Bruma Freight the weighted winner is `build` and the lowest operating total is `vendor_b`. The simulated [EST] 3-year operating gap is 57,316.07 USD (build 129,433.40, vendor_b 72,117.33). Including the modeled exit fee, the same pair differs by 2,683.93 USD the other way. Those dollars are simulated.

On the fictional refund-desk assumptions the sketch shows about USD 12,775 of net monthly savings in steady state and a payback of about 17 months [EST inputs, simulated output]. The pessimistic set never pays back. See [docs/BUSINESS_CASE.md](docs/BUSINESS_CASE.md).

## Results

Decision figures below are calculated from illustrative [EST] inputs. First published 2026-10-17, package 0.2.0, Python 3.12.3, command `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit`. The same command on 2026-10-22 printed the same stability fields (`67.86` and `100.00`) and `BOTH EVAL GATES PASSED`. That command checks the calculator. It does not score an assistant.

ROI figures are simulated outputs of `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_and_build_vs_buy roi publish-docs` (wall time 0.751 seconds, 2026-10-17). Nothing here is a vendor price.

### Build versus buy

| Case | Winner | Score [EST] | Winner stability | Rank stability | Scenarios |
| --- | --- | ---: | ---: | ---: | ---: |
| Bruma Freight support agent | `build` | 3.7000 | 67.86% | 67.86% | 28 |
| Cedro Records document assistant | `build` | 4.3600 | 100.00% | 100.00% | 28 |

Bruma Freight base cash (simulated, [EST], horizon 3, input date 2026-10-17). Same numbers as `docs/examples/bruma-freight-report.md`.

| Option | Weighted score [EST] | 3-year operating USD [EST] | 3-year USD with exit [EST] | Build crossover |
| --- | ---: | ---: | ---: | --- |
| `build` | 3.7000 | 129433.40 | 129433.40 | — |
| `vendor_a` Harborline Desk | 3.6200 | 175259.79 | 203259.79 | operating year 2 |
| `vendor_b` Quayloop | 3.0200 | 72117.33 | 132117.33 | operating: none; with exit: year 3 |

Smallest one-at-a-time flip on Bruma Freight: raising the time-to-value weight by 0.031 (from 0.20 to 0.231) makes `vendor_a` the winner.

Cedro Records base cash, same dating and labels:

| Option | Weighted score [EST] | 3-year operating USD [EST] | 3-year USD with exit [EST] | Build crossover |
| --- | ---: | ---: | ---: | --- |
| `build` | 4.3600 | 80751.76 | 80751.76 | — |
| `vendor_a` Folio Cloud | 3.4200 | 107428.39 | 127428.39 | operating year 2 |
| `vendor_b` Parchment Lane | 2.3800 | 54776.98 | 99776.98 | operating: none; with exit: year 3 |

On both cases the weighted winner is `build` and the lowest operating total is `vendor_b`.

Local timing of the decision report, not model latency: 30 sequential runs of `python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out /tmp/lat-N.md` on 2026-10-17, package 0.2.0, Python 3.12.3, sorted, index `round(p/100*(n-1))` (indexes 14 and 28). Result: p50 0.152 s, p95 0.158 s. Not re-timed on 2026-10-22.

### Fictional refund desk (Puerto Gris Parcel Co.)

| Metric | Base | Pessimistic | Optimistic |
| --- | --- | --- | --- |
| Net monthly savings, steady state | USD 12,775.15 | USD -1,700.00 | USD 31,982.79 |
| Payback | 17.08 months | never | 3.85 months |
| 3-year NPV | USD 180,923.12 | USD -350,556.83 | USD 874,596.57 |
| Break-even volume | 412.43 items/month | none | (see JSON) |
| Cost per completed item, with review | USD 1.34 | | |
| Quality-adjusted savings per item | USD 6.06 | | |
| Residual error cost per item | USD 0.50 | | |
| Illustrative agent cost per run | USD 0.0051 | | |

Monte Carlo, 2000 draws, seed 42, base ranges (simulated):

| | P10 | P50 | P90 |
| --- | --- | --- | --- |
| 3-year NPV | USD -5,178.08 | USD 167,292.34 | USD 380,101.33 |
| Net monthly | USD 7,382.58 | USD 12,884.66 | USD 20,553.62 |

Largest one-at-a-time NPV swings: `volume_per_day`, `manual_minutes_per_item`, `loaded_cost_per_hour`.

### Personal example: weekly report

| Metric | Base | Pessimistic | Optimistic |
| --- | --- | --- | --- |
| Net monthly savings | USD 168.96 | USD -67.71 | USD 524.96 |
| Payback | 1.78 months | never | 0.57 months |
| 3-year NPV | USD 5,114.00 | USD -2,469.59 | USD 16,521.42 |

The pessimistic personal case is "your hour is cheap and you still spend an hour reviewing". The base case is not a recommendation to buy a subscription.

## Use cases, governance and business strategy

### 1. Use cases

Client-style rows use a fictional organisation. Personal rows are sketches. Status is explicit.

| Use case | Status | Problem | Who approves | Gated effects | How this repo handles it |
| --- | --- | --- | --- | --- | --- |
| Support-agent build vs buy, Bruma Freight (fictional) | Implemented | A freight desk wants drafts for shipment-exception tickets and has to choose build, Vendor A, or Vendor B | The decision owner accepts or rejects the ADR. The CLI cannot accept it | None. The kit writes Markdown | `examples/bruma_freight`, `decide report`, [ADR bvb-0002](docs/adr/bvb-0002-bruma-freight-support-agent.md) |
| Document assistant, Cedro Records (fictional) | Implemented | An archive cooperative wants cited answers from internal binders | The decision owner accepts or rejects the ADR | None. No index is built | `examples/cedro_records`, [ADR bvb-0003](docs/adr/bvb-0003-cedro-records-document-assistant.md) |
| Refund back-office agent ROI at Puerto Gris Parcel Co. (fictional) | Implemented | Manual refund decisions are slow; review and residual errors can eat the gain | A person reading the assumptions. The model never approves | No external action. The report is a file | `assumptions/refund_desk.yaml`, monthly model, one-pagers |
| Should I automate my weekly report? | Implemented as a personal example | An hour of writing versus a draft you still read | You. The model does not subscribe to anything | No purchase, no send | `assumptions/weekly_report.yaml` |
| Contact-center deflection economics | Design only | Handle time, reopen rate, and the cost of a bad deflection are not in this repo | Would be the operations owner | Would gate any routing change. Not built | Named in `docs/SCOPE.md`. No runnable case |
| Document-processing agent ROI | Design only | Page volume and exception rate have to be calibrated per document type | Would be the process owner | Would gate writes into a system of record. Not built | Named only |
| Voice-agent platform selection | Design only | Telephony adds latency, number ownership, and recording | Would still be a named decision owner | Placing a call, buying a number | [docs/design-only/voice-agent-platform.md](docs/design-only/voice-agent-platform.md) |
| AI coding assistant for a side project | Design only | A person choosing a coding assistant for their own repo | The person | Account spend, repository access | [docs/design-only/personal-coding-assistant.md](docs/design-only/personal-coding-assistant.md) |
| DIY vs SaaS for a personal automation | Design only | A personal recurring task that could be a script or a subscription | The person | Sending messages, paying a subscription | [docs/design-only/personal-automation.md](docs/design-only/personal-automation.md) |
| Cost of my own AI subscriptions versus benefit | Design only | A subscription is a fixed cost; the benefit depends on which tasks move | You | Would not charge a card. Not built | `monthly_run_cost` in the weekly example is an [EST] slice, not a plan price |

### 2. Governance checklist

| Control | Where |
| --- | --- |
| ROI inputs are illustrative, each with `illustrative: true` and a rationale that contains `[EST]` | `assumptions/*.yaml`, `src/roi_and_build_vs_buy/roi/assumptions.py`, shared tag in `src/roi_and_build_vs_buy/assumptions.py` |
| Decision weights sum to 1; scores are integers 1–5 with a rationale | `src/roi_and_build_vs_buy/build_vs_buy/matrix.py`, checked again in `src/roi_and_build_vs_buy/evalkit/decide_gate.py` |
| Every TCO number has source, date, and estimate; a USD figure marked real without an https URL is rejected | `src/roi_and_build_vs_buy/build_vs_buy/prices.py` |
| Cases are marked fictional | `load_case`, `load_weights`, `load_tco` |
| Human approval | Reports say the tools do not approve. Decision ADRs stay `proposed`. There is no approve command |
| Traceability | JSON logs (`logging_setup.py`); JSONL traces (`evalkit/trace.py`); inputs and generated ADRs in git. One-pagers name the command, version, and generation time |
| Risks | [docs/RISKS.md](docs/RISKS.md) |
| Costs | [docs/COST.md](docs/COST.md) |
| Value plan | [docs/BUSINESS_VALUE.md](docs/BUSINESS_VALUE.md). It restates the case files. It does not add a second volume |
| Incident and rollback | [docs/RUNBOOK.md](docs/RUNBOOK.md) |
| Invariants instead of scripted tool paths | `evalkit/roi_invariants.py` and `evalkit/decide_gate.py` |
| Paid calls cannot happen in CI | `ROI_ENABLE_REAL_PROVIDER` and `DECIDE_REAL_PROVIDER` default to 0. The ROI real provider has no HTTP client. The decision eval ignores the real-provider flag and uses a cassette. Tests block sockets |
| Secrets | `src/roi_and_build_vs_buy/secretscan.py`, `.env.example`, `.gitignore`. Prefix shapes include `xai-`, `sk-` (also `sk-proj-`), `sk-ant-`, `sk_`, `ghp_`, `github_pat_`, `AKIA`, a `Bearer` token, and private-key headers |
| Forced red gates | `make eval-regression` exits 1 only when both forced regressions fail. CI treats a zero from that target as a failure |

Not covered yet: live data connectors, a dashboard, identity for a multi-user app, a quote feed, tax, currency conversion, queueing, and any link to a ledger.

### 3. Business strategy

The path is a decision, then a business case, then a phased rollout. Discovery comes first ([docs/DISCOVERY.md](docs/DISCOVERY.md)), not a model name.

Phase 0, implemented here: score build versus buy on one workflow, write the ADR, and run the monthly ROI on the option you would actually fund. Both stay in shadow. The files sit next to the current process and do not change it.

Phase 1, design only: replace `[EST]` inputs with measurements, one field at a time, and keep the old file in git. A connector, if one is added later, would refresh a YAML that a person still commits.

Phase 2, design only: a dashboard or a live effect (sending a reply, moving a ticket, placing a call). That needs an owner and a human gate. Nothing in this repository is that gate.

A person owns the assumption files. Finance owns the discount rate and any real price. The process owner owns review rate, error cost, seats, and exit. This repo does not own a decision. Scope is in [docs/SCOPE.md](docs/SCOPE.md). Success metrics are in [docs/METRICS.md](docs/METRICS.md). The value plan is in [docs/BUSINESS_VALUE.md](docs/BUSINESS_VALUE.md).

## Business value

The buyer in the worked examples is fictional (Puerto Gris Parcel Co., Bruma Freight, Cedro Records) or personal (the weekly report). The problem is a slide that picks build or buy on one score, and a token price that ignores review time and residual errors.

Full plan: [docs/BUSINESS_VALUE.md](docs/BUSINESS_VALUE.md). It reuses [docs/BUSINESS_CASE.md](docs/BUSINESS_CASE.md), [docs/COST.md](docs/COST.md), and [docs/METRICS.md](docs/METRICS.md). It does not add a second set of volumes, and it does not publish a new ROI percentage.

**What the repo measures:** the calculator, the gates, the secret scan, the type check, and a recorded 23-case eval bill that is not applied to the case inputs. **What it simulates:** NPV, payback, and the cash totals, from [EST] inputs. Winner stability is calculated from those inputs. It is not a field rate.

On the refund desk the base case is SIMULATED: net monthly savings USD 12,775.15, payback 17.08 months, 3-year NPV USD 180,923.12. The pessimistic scenario never pays back (NPV USD -350,556.83). Running the default path costs USD 0.

## Proof

**MEASURED 2026-10-22.** Python 3.12.3. pytest 9.1.1. pytest-cov 7.1.0. coverage 7.17.0. Package `roi_and_build_vs_buy` 0.2.0. Tree `6452c09` (the parent of this documentation change; this change does not edit Python under `src/` or `tests/`).

Command:

```bash
python3 -m pytest --cov=roi_and_build_vs_buy --cov-report=term-missing --cov-fail-under=80
```

| Result | Value |
| --- | --- |
| Tests | 80 passed |
| Line coverage | 90.98% |
| What the tool printed | `Total coverage: 90.98%` |
| Same report, TOTAL row | 2,905 statements, 262 missed, displayed as 91% (the table rounds) |
| Warning on that run | `CoverageWarning: Module roi_and_build_vs_buy was previously imported, but not measured` |

The 90.98% figure is the total pytest-cov printed on a clean tree (no `out/` directory). That is the line-coverage number for this section. The table's 91% is the same run, rounded. An earlier run on 2026-10-17 recorded the same 80 passed and 90.98% (Python 3.12.3, package 0.2.0) and did not name a pytest version.

A second run the same day, after `out/traces/eval.jsonl` already existed, printed `Total coverage: 91.02%` (2,905 statements, 261 missed). The extra covered line is `trace.unlink()` in `src/roi_and_build_vs_buy/evalkit/decide_run.py`, which runs only when that file is already present. The 90.98% figure is the clean-tree result.

Other checks on the same date, same Python, package 0.2.0:

| Check | Result | Command |
| --- | --- | --- |
| Both eval gates | exit 0, printed `BOTH EVAL GATES PASSED`. Bruma stability `67.86`, Cedro `100.00` | `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit` |
| Forced ROI regression | exit 1, savings identity and break-even failed | `ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.roi_regression` |
| Forced decision regression | exit 1, `golden_winner: expected build got vendor_b`, stability 59.09 below 67.86 | `DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.decide_regression` |
| Secret scan | `{"ok": true, "findings": 0}` | `python3 -m roi_and_build_vs_buy.secretscan .` |
| Types | no issues in 55 source files (mypy 2.4.0) | `python3 -m mypy` |

The 59.09% line is the same calculator on illustrative weights edited on purpose. It is not an assistant failing a task. Publish wall time (0.751 seconds) and decision-report latency (p50 0.152 s, p95 0.158 s) stay dated 2026-10-17. They were not re-timed on 2026-10-22.

## What this does NOT prove

- It does not prove a company saved USD 180,923.12, paid back in 17.08 months, or chose to build. Those figures are SIMULATED or calculated from [EST] inputs.
- It does not prove that building is the right choice. 67.86% is 19 of 28 weight shifts on one fictional file. A shift of 0.031 on time-to-value flips Bruma Freight to `vendor_a`.
- It does not prove a model is accurate, cheap, or safe to leave unreviewed. The default path does not call a model. The 23-case xAI bill in `assumptions/measured_eval_run_cost.yaml` is a recorded eval-run total (US$0.036–0.037 and US$0.072, commit `c1efdfd`, 2026-10-17). It is not a per-refund cost, and dividing it by 23 is [EST] and is not applied.
- It does not prove a review rate, a residual error rate, or a forecast error on a real desk. Those rows in [docs/METRICS.md](docs/METRICS.md) are UNVERIFIED.
- It does not prove the pessimistic case is impossible. On the refund file that case never pays back (NPV USD -350,556.83). On the Monte Carlo, P10 NPV is USD -5,178.08.
- A green test suite is not a rollout. [docs/METRICS.md](docs/METRICS.md) says this in those words.
- It does not call a model vendor. `ROI_ENABLE_REAL_PROVIDER=1` still has no HTTP client. `DECIDE_REAL_PROVIDER=1` is off, and the eval path does not construct the HTTP adapter.
- It does not read a CRM, a ticket queue, a ledger, or a price page.
- It does not use client, employer, or personal data. Names in the examples are fictional.
- It does not approve a purchase, a refund, a routing change, a subscription, or a vendor contract.
- It does not provide a dashboard.
- It does not model tax, depreciation schedules, currency, or hiring delays beyond the ramp fraction and the build-overrun scenario.
- It does not evaluate spreadsheet formulas inside CI. The workbook is live when you open it in a spreadsheet.

### Design-only vs implemented

| Piece | State |
| --- | --- |
| Weighted matrix, winner stability, 3-year TCO, scenarios, break-even year, CLI reports | Implemented |
| Bruma Freight and Cedro Records, generated reports and ADRs | Implemented |
| Monthly NPV, payback, break-even, unit cost, quality adjustment | Implemented |
| Tornado, pessimistic/base/optimistic, seeded PERT/triangular Monte Carlo | Implemented |
| CSV, formula XLSX, Markdown, HTML, inline SVG, EN/ES one-pagers | Implemented |
| Two invariant gates and two forced regressions | Implemented |
| Shared `[EST]` tag, one secretscan, one logger, one retry module, one trace | Implemented |
| Measured 23-case eval bill | Recorded in `assumptions/measured_eval_run_cost.yaml` and not applied to the invented inputs |
| Contact-center deflection, document-processing ROI, personal subscription versus benefit | Design only |
| Voice platform, personal coding assistant, personal automation | Design only |
| Live connectors, dashboards, procurement, questionnaire automation | Design only. Checklist: [docs/security-questionnaire-checklist.md](docs/security-questionnaire-checklist.md) |

## Decisions

ROI:

- [ADR 0001](docs/adr/0001-monthly-pure-python.md) — monthly model, pure Python
- [ADR 0002](docs/adr/0002-quality-adjusted-savings.md) — quality-adjusted savings
- [ADR 0003](docs/adr/0003-break-even-is-operating-volume.md) — break-even is operating volume
- [ADR 0004](docs/adr/0004-invariants-and-providers-off.md) — invariants, providers off
- [ADR 0005](docs/adr/0005-xlsx-formulas-and-csv.md) — formulas in XLSX, values in CSV
- [ADR 0006](docs/adr/0006-assumption-file-is-the-source.md) — the YAML file is the only numeric source

Build versus buy (filenames are prefixed so they do not collide with the ROI ADRs; the ids inside the generated files stay 0002 and 0003):

- [Template](docs/adr/bvb-0001-build-vs-buy-template.md)
- [Bruma Freight](docs/adr/bvb-0002-bruma-freight-support-agent.md)
- [Cedro Records](docs/adr/bvb-0003-cedro-records-document-assistant.md)
- [Invariant evals and dated prices](docs/adr/bvb-0004-invariant-evals-and-dated-prices.md)

## How to reproduce

Cost of the default path: **zero**. No API key. No network in tests.

```bash
python3 -m pip install -e ".[dev]"
python3 -m ruff check . && python3 -m ruff format --check .
python3 -m mypy
python3 -m pytest --cov=roi_and_build_vs_buy --cov-report=term-missing --cov-fail-under=80
ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit
ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.roi_regression          # must exit 1
DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.decide_regression       # must exit 1
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python3 -m roi_and_build_vs_buy roi demo
python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma-freight-report.md
python3 -m roi_and_build_vs_buy.secretscan .
```

`make setup`, `make lint`, `make typecheck`, `make test`, `make eval`, `make eval-regression`, `make demo`, and `make secrets` call those commands. `make test` is `python3 -m pytest`, which already passes `--cov` and `--cov-fail-under=80` from `pyproject.toml`. `make eval-regression` exits 1 when both forced regressions fail, and exits 0 when either one passes. CI treats that zero as a failure. Make may be absent; the `python3 -m` lines are enough.

Configuration is environment-only. See `.env.example`. This program does not auto-load a `.env` file.

## Next steps

- Replace illustrative `[EST]` inputs with measurements, one field at a time. Steps: [docs/REPLACE_THE_ASSUMPTIONS.md](docs/REPLACE_THE_ASSUMPTIONS.md). Adapting both modules to a real client: [docs/ADAPT_TO_A_REAL_CLIENT.md](docs/ADAPT_TO_A_REAL_CLIENT.md).
- The measured 23-case eval bill is not a per-item cost. A per-item override is a different file with `status: measured` and `roi run --measured-cost`. Do not paste a price-page number and call it measured.
- Design-only cases stay out of the result tables until their parameters exist.
- A dashboard, a live connector, or a quote feed is a later phase.

## Docs

- [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) — plain-language walkthrough
- [docs/BUSINESS_VALUE.md](docs/BUSINESS_VALUE.md) — value plan. No new volumes. Labels are MEASURED, [EST], SIMULATED, or UNVERIFIED
- [docs/BUSINESS_CASE.md](docs/BUSINESS_CASE.md)
- [docs/DISCOVERY.md](docs/DISCOVERY.md)
- [docs/SCOPE.md](docs/SCOPE.md)
- [docs/RISKS.md](docs/RISKS.md)
- [docs/METRICS.md](docs/METRICS.md)
- [docs/COST.md](docs/COST.md)
- [docs/RUNBOOK.md](docs/RUNBOOK.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/ADAPT_TO_A_REAL_CLIENT.md](docs/ADAPT_TO_A_REAL_CLIENT.md)
- [docs/REPLACE_THE_ASSUMPTIONS.md](docs/REPLACE_THE_ASSUMPTIONS.md)
- [docs/PROVENANCE.md](docs/PROVENANCE.md)
- [docs/ONE_PAGER_EN.md](docs/ONE_PAGER_EN.md), [docs/ONE_PAGER_ES.md](docs/ONE_PAGER_ES.md)
- [docs/examples/bruma-freight-report.md](docs/examples/bruma-freight-report.md), [docs/examples/cedro-records-report.md](docs/examples/cedro-records-report.md)
- [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md)

## Authorship and how this was built

This repository was built with AI-assisted development.

**What Diego Lescano set:**

- The problem and the scope: the disagreement between a weighted score and the cash total, then a monthly ROI that can fail to pay back, and what the repo must not claim.
- The governance requirements: assumption tags, a human reading the file, traceability, risks, costs, rollout, and metrics.
- The engineering standards: Python, tests, CI, fictional examples only, no client or employer data.
- What is allowed to be called measured, and what stays illustrative.

**What AI coding agents did:**

- Wrote most of the code, tests, and documentation from those briefs, under review.

**What this repo does not claim:**

- It is not a deployed service. The worked examples are fictional.
- Simulated NPV and winner stability come from illustrative inputs. They are not a result a company achieved.
