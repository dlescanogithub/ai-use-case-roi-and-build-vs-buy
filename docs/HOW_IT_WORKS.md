# How it works (plain language)

This is a calculator with two modules. It is not an agent that talks to customers, and it does not call any paid model. This walkthrough is for engineers and buyers. It states the whole path plainly: first you decide whether you build or buy, then you look at whether the case works out in money, and only then you talk about a phased rollout. The rollout in this repo stays in shadow: it writes files, and it does not touch a real process.

The code is in English. The package is called `roi_and_build_vs_buy`, version 0.2.0. The command is `python -m roi_and_build_vs_buy` with two subcommands: `decide` and `roi`.

The value plan, in English and with no new numbers, is in `docs/BUSINESS_VALUE.md`. On 2026-10-22, with Python 3.12.3 and pytest 9.1.1, `python3 -m pytest --cov=roi_and_build_vs_buy --cov-report=term-missing --cov-fail-under=80` printed 80 passed tests and `Total coverage: 90.98%` on a clean tree, with no `out/` folder. The table from that run rounds the same total to 91% (2905 statements, 262 not covered). It is the same count as on 2026-10-17. If the trace file was already there, the same command printed 91.02% because the `unlink` of that trace is included. It is not a company's savings.

## Two analogies, in order

### 1. Rent or build

Imagine you need a place to live.

- **Build (build)** takes longer, and you put a lot of money in at the start. After that the house is yours. Maintenance stays with you.
- **Rent (buy)** and you move in faster. You pay every month. The owner can raise the rent. Leaving means a move, and sometimes a clause.

An internal agent is similar. Building it is a team, a test set, and a small cost per run. Buying it is seats, a usage price, and an exit that hurts if the format is closed.

This module does not pick the house. It builds the sheet: scores, weights, money over 3 years, and the question "how far would one weight have to move for the other option to win?".

### 2. The dripping tap

Once you have leaned toward one option, look at whether the monthly savings are enough.

- Implementation is the money and the hours on day one.
- Monthly savings are the water you stop pouring away, minus what the replacement part that wears out costs you.
- Payback is how many months it takes to gather again what you spent at the start.
- Break-even volume is how many buckets you have to save per month so the repair does not leave you at a loss, still without counting the day-one spend.
- Sensitivity is turning one knob. The tornado chart shows which one moves the result the most.
- Monte Carlo is rolling the dice many times and looking at percentile 10, percentile 50, and percentile 90. It is not a promise.

Notice this: if human review eats almost all of the time you "were saving", the tap is still dripping. The model puts that time inside the calculation, not in a footnote.

## Step by step

1. You open a `decide` case folder. Inside there are three YAML files: `weights.yaml`, `scores.yaml`, `tco.yaml`. The two examples are **Bruma Freight** (a shipment-exception desk, an invented company) and **Cedro Records** (an invented archive cooperative).
2. The weights are eight criteria and they have to sum to 1: control, time to value, 3-year TCO, vendor risk, security and compliance, maintainability, extensibility, exit cost.
3. Each option has a score from 1 to 5 per criterion, with a sentence that explains why. **Higher is better**, including on cost and on risk. An illustrative number is tagged `[EST]`.
4. `decide score` multiplies weight by score and sorts. If there is a tie, the id breaks it.
5. Sensitivity moves one weight at a time (−0.10, −0.05, +0.05, +0.10), drops the shifts that would leave a weight outside 0.01–0.90, rescales the rest, and ranks again. On Bruma, with these illustrative scores, that is 19 of 28, or 67.86%. It then searches, in steps of 0.001, for the smallest change that flips the winner.
6. `decide tco` projects the money over 3 years. Exit cost is not in the operating total: it is added in the last year, in the "With exit" column.
7. The report puts the two stories together. If the matrix winner and the cheapest option in cash are different, it says so. That happens in both examples: `build` wins on score and `vendor_b` is cheaper in operating cost.
8. The ADR stays `proposed`. A person accepts it. The command does not buy anything.
9. If that option still holds, you open an ROI YAML. Every number has a reason and has to say `[EST]`. The examples are the refund desk at Puerto Gris Parcel Co. (invented) and a personal weekly report.
10. For each item the ROI calculates the manual cost, the agent cost (tokens times an illustrative price, or a measured cost if you pass a different file), and the quality-adjusted savings.
11. Steady-state net monthly savings are volume × savings per item − monthly fixed cost. The fixed cost is paid in full from month 1. Adoption rises in a straight line during the ramp.
12. Payback can say **never**. The 3-year NPV discounts the cash flows. The tornado moves one assumption at a time. Monte Carlo uses a seed.
13. It writes Markdown, HTML, an SVG, a CSV, and an XLSX with formulas. It does not send mail and it does not approve anything.
14. `python -m roi_and_build_vs_buy.evalkit` runs both gates. The ROI gate rechecks the savings identity. The `decide` gate checks that the weights sum to 1, that the winner matches `evals/golden/decisions.json`, that TCO does not fall when you raise volume or hours, that the cassette costs 0, and that the trace does not record an external action. It does not evaluate an assistant.
15. There are two regressions that **have to fail**. `evalkit.roi_regression` inserts a deliberately wrong savings formula. `evalkit.decide_regression` changes the Bruma weights: the winner becomes `vendor_b` and stability lands at 59.09%, under the floor of 67.86%. CI checks that both fail. 67.86% is not a probability and it is not a success rate on a real desk.

The phased rollout is in `docs/SCOPE.md`. Phase 0 is this calculator. A connector or a dashboard is not built.

## Glossary

| Word | What it means here |
| --- | --- |
| [EST] | Illustrative assumption. It did not come from a real system |
| Simulated | This program calculated it from those assumptions |
| Weighted matrix | Scores multiplied by weights that sum to 1 |
| TCO | Total cost over the horizon, here 3 years |
| Winner stability | Percentage of the fixed grid where first place holds |
| Quality-adjusted savings | The savings after subtracting the cost of the errors that still remain |
| Break-even volume | Items per month where net monthly savings are zero. Implementation is not included |
| Payback | Months until implementation is recovered. It can be "never" |
| NPV | Net present value of the horizon cash flows, minus implementation |
| Tornado | Which assumption, moved alone, changes NPV the most |
| Cassette | A recorded file. If the id is missing, it fails. There is no live call |
| Invariant | A property that has to be true, not a script of calls |

## Limits, said plainly

- Read the YAML before you read the ranking. If the score is inflated, the ranking is too.
- Bruma wins by a little: 3.70 against 3.62. Raising the time-to-value weight by 0.031 makes Vendor A win.
- The base NPV of the refund desk came out **USD 180,923.12** on 2026-10-17 with the command in `docs/results/refund_desk.json`, and the pessimistic scenario **never pays back**.
- There is no client data. Puerto Gris, Bruma, and Cedro are invented.
- The per-token price in the ROI YAML is illustrative. It is not a vendor price list.
- A security score records what the fictional case notes say. It is not a certification.
- The Excel file has live formulas, but this repo does not execute them.
- It does not predict the queue, the SLA, or whether people will use the tool.
- It does not decide. You decide.

## A five-minute walkthrough

1. Run `python -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma.md`.
2. Read the ranking and the sentence where the matrix and the cash model disagree.
3. Read the time-to-value flip (+0.031).
4. Run `python -m roi_and_build_vs_buy roi demo` and read the refund-desk payback next to the scenario that never pays back.
5. Run `python -m roi_and_build_vs_buy.evalkit.decide_regression` and check that it exits with error `golden_winner`. That red is the proof that the regression can fail.

The English README has the Proof section for the run on 2026-10-22. Both gates exited 0 again that day, and both forced regressions exited 1 again. The 0.751 second time for `publish-docs` is still the 2026-10-17 figure: it was not re-timed.
