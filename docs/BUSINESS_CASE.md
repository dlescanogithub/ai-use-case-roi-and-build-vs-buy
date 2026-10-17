# Business case

Fictional sketch only. Puerto Gris Parcel Co., Bruma Freight, and Cedro Records do not exist. Every input is [EST]. Outputs below are simulated or calculated by package 0.2.0 on 2026-10-17.

The story is one sequence. Score build against buy. If an option is still worth talking about, run the monthly ROI on that option. Keep both files in shadow until a person accepts them.

## Decision: build versus buy

On the committed Bruma Freight inputs the weighted winner is `build` (score 3.7000) and the lowest 3-year operating total is `vendor_b` (Quayloop).

| Question | Calculated answer | Source |
| --- | --- | --- |
| Winner stability | 67.86% (19 of 28) | `python3 -m roi_and_build_vs_buy.evalkit`, 2026-10-17, package 0.2.0 |
| Operating gap, build versus vendor_b | 57,316.07 USD, vendor_b lower | `docs/examples/bruma-freight-report.md`. Build 129,433.40, vendor_b 72,117.33 |
| Same pair including exit | 2,683.93 USD the other way | same report. Build 129,433.40, vendor_b with exit 132,117.33 |
| Smallest flip | time-to-value weight +0.031 makes `vendor_a` win | same report |

Those dollars are simulated [EST]. Cedro Records has the same shape of disagreement (weighted winner `build`, lowest operating total `vendor_b`) with winner stability 100.00% on the same grid. Running the kit costs 0 USD of API spend.

The point of the kit is that disagreement. A cheap operating total can still be the wrong build once exit, control, and risk are scored. A high score can still fail a payback test. That second test is the ROI model.

## ROI model [EST]

On the base refund-desk assumption file:

| Question | Simulated answer | Source |
| --- | --- | --- |
| Net monthly savings in steady state | USD 12,775.15 | `docs/results/refund_desk.json` |
| Payback | 17.08 months | same file |
| 3-year NPV at a 10% [EST] discount rate | USD 180,923.12 | same file |
| Does the pessimistic set pay back? | No | same file, NPV USD -350,556.83 |

Command that wrote the file: `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_and_build_vs_buy roi publish-docs` (0.751 seconds, 2026-10-17, package 0.2.0, Python 3.12.3).

This is not a forecast, a quote, or evidence that a company saved this money. It is the arithmetic of the assumption file. Change the review rate or the volume and the sign can flip. The Monte Carlo P10 NPV on that same run was negative (USD -5,178.08), so a slice of the assumption ranges does not pay back inside three years.

## Who would use it

A person preparing a pilot conversation. They bring the YAML, not a slide with one number. Finance owns the discount rate and any real price. The process owner owns minutes, error cost, review rate, seats, and exit. Nobody in this repository is that person for a real company.

## What would have to be true

For the Bruma sketch, someone would need to believe the illustrative scores and the exit dollars, knowing that a 0.031 move in one weight flips the winner. For the refund sketch to be even worth a pilot conversation, someone would need to believe the [EST] volume, the minutes, and a review rate that does not climb to the pessimistic 0.85. Those beliefs are not checked here.

## Personal example

The weekly-report case is the same ROI arithmetic on a smaller file. Base NPV USD 5,114.00, payback 1.78 months. Pessimistic NPV USD -2,469.59 and it never pays back, if the assumed value of an hour is low and the review takes as long as writing. Details: `docs/results/weekly_report.json`.

## Phased rollout

Phase 0 is the two files: the decision report and the ROI one-pager, both labeled [EST]. Phase 1 would replace inputs with measurements. Phase 2 would be a dashboard or a live effect, and it is not started. See [SCOPE.md](SCOPE.md).
