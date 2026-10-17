# Business case

Fictional sketch only. Puerto Gris Parcel Co. does not exist. Every input is [EST]. Outputs below are simulated by package 0.1.0 on 2026-10-17.

## Problem

A returns desk spends minutes on each refund. An agent can draft the decision. The draft is not free: someone still reviews a share of cases, some errors remain, the platform has a monthly cost, and the build is paid up front. A token price on its own does not answer whether the desk should do it.

## ROI model [EST]

The model is the monthly calculator in this repo. On the base assumption file:

| Question | Simulated answer | Source |
| --- | --- | --- |
| Net monthly savings in steady state | USD 12,775.15 | `docs/results/refund_desk.json` |
| Payback | 17.08 months | same file |
| 3-year NPV at a 10% [EST] discount rate | USD 180,923.12 | same file |
| Does the pessimistic set pay back? | No | same file, NPV USD -350,556.83 |

Command that wrote the file: `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_model.cli publish-docs`.

This is not a forecast, a quote, or evidence that a company saved this money. It is the arithmetic of the assumption file. Change the review rate or the volume and the sign can flip. The Monte Carlo P10 NPV on that same run was negative (USD -5,178.08), so a slice of the assumption ranges does not pay back inside three years.

## Who would use it

A person preparing a pilot conversation. They bring the YAML, not a slide with one number. Finance owns the discount rate. The process owner owns minutes, error cost and review rate. Nobody in this repository is that person for a real company.

## What would have to be true

For the base sketch to be even worth a pilot conversation, someone would need to believe the [EST] volume, the minutes, and a review rate that does not climb to the pessimistic 0.85. Those beliefs are not checked here.

## Personal example

The weekly-report case is the same arithmetic on a smaller file. Base NPV USD 5,114.00, payback 1.78 months. Pessimistic NPV USD -2,469.59 and it never pays back, if the assumed value of an hour is low and the review takes as long as writing. Details: `docs/results/weekly_report.json`.
