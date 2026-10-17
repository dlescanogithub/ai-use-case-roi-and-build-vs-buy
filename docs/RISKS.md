# Risks

Owners are roles. No real person is assigned. Probability and impact are labels for this portfolio piece, not a measured risk study.

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Garbage in: a guessed minute or error rate is treated as fact | High | High | Every rationale must contain `[EST]`. Reports say simulated. The one-pager says to replace assumptions before anyone treats NPV as a plan | Person who edits the YAML |
| Optimism bias: base case only, pessimistic ignored | High | High | Named pessimistic scenario is required. On the refund file it never pays back (measured output 2026-10-17, NPV USD -350,556.83) | Person who presents the number |
| Review cost ignored | Medium | High | Review minutes and review rate are required inputs. Quality-adjusted savings subtract residual errors | Process owner |
| Illustrative token price quoted as a vendor price | Medium | Medium | Prices in the YAML are tagged [EST] and the rationale says they are not a price page. The measured-cost slot rejects stubs | Person who edits the YAML |
| Adoption slower than the ramp | Medium | Medium | Ramp is its own parameter and a tornado input. Payback uses the ramp, not a steady-state shortcut | Process owner |
| Fixed cost understated (on-call, monitoring, rework of the integration) | Medium | High | `monthly_run_cost` is explicit and charged from month 1. The runbook says to version the file when it changes | Operator of the pilot, later |
| Discount rate disagrees with finance | Medium | Medium | The rate is an input, not a hidden constant. Discovery question 10 | Finance partner |
| Model used as an automatic go decision | Medium | High | No approve command. Trace actions are only read, compute, replay, write. The eval gate fails on unapproved actions | Person who asked for the number |
| Secret committed | Low | High | `.env` is gitignored. `secretscan` runs in CI. No vendor client, so there is no key to embed | Repository owner |
| Formula bug that still "looks internally consistent" | Low | High | The eval gate restates the savings identity. `make eval-regression` injects a wrong formula and must fail | Repository owner |
| Spreadsheet formulas drift from Python | Medium | Medium | CSV holds the Python values. XLSX formulas are documented in ADR 0005. CI does not execute Excel | Person who opens the workbook |
| Monte Carlo read as a confidence interval from real data | Medium | High | Draws are labeled simulated. Ranges are the low/high in the YAML, not a sample from production | Person who presents the number |

Not covered: legal review of automated refunds, customer harm from a wrong refund, model bias, and security of a future connector. Those belong to a real deployment, which this repo is not.
