# Risks

Owners are roles. No real person is assigned. Probability and impact are labels for this repository, dated 2026-10-17, not a measured risk study. "Decision owner" means the person who can accept an ADR. "YAML owner" means the person who edits the case files.

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Garbage in: a guessed minute, score, or error rate is treated as fact | High | High | ROI rationales must contain `[EST]`. Decision cells require a rationale. Reports say simulated | YAML owner |
| Optimism bias: base case only, pessimistic ignored | High | High | The refund pessimistic scenario never pays back (simulated output 2026-10-17, NPV USD -350,556.83). Bruma's lead is 0.08 points; time-to-value +0.031 flips it | Person who presents the number |
| Vendor lock-in understated | Medium on a close case | High: the exit shows up in year 3 | `exit_cost` is its own criterion and a separate cash column. On Bruma, `vendor_b` is the operating-cost winner and loses once exit is included | Decision owner |
| Price drift above the assumption | Medium | Medium | Re-run `decide tco` when a renewal arrives. The ADR revisit list includes an increase above `annual_price_increase` | YAML owner |
| Review cost ignored | Medium | High | Review minutes and review rate are required ROI inputs. Quality-adjusted savings subtract residual errors | Process owner |
| Illustrative token price quoted as a vendor price | Medium | Medium | YAML prices are tagged [EST]. The measured-cost slot rejects stubs and refuses the 23-case eval bill | YAML owner |
| Scores that encode a hope instead of a constraint | Medium | High | Rationales are required. Discovery asks where text lives and what export exists | Decision owner |
| A real price pasted without a source | Low if the loader is used | Medium | The TCO loader rejects a bare number and rejects `estimate: false` without an https URL and a date | YAML owner |
| Adoption slower than the ramp | Medium | Medium | Ramp is its own parameter. Payback uses the ramp, not a steady-state shortcut | Process owner |
| Fixed cost understated | Medium | High | `monthly_run_cost` is charged from month 1 | Operator of a later pilot |
| Discount rate disagrees with finance | Medium | Medium | The rate is an input. Discovery covers it | Finance partner |
| Model used as an automatic go decision | Medium | High | No approve command. ADRs stay `proposed`. Eval gates fail on unapproved actions | Person who asked for the number |
| Treating simulated dollars as a budget | Medium | High | Reports repeat simulated and [EST] | Whoever presents the report |
| Golden file edited to match a bad weight change | Low | High | The forced-regression fixture must fail in CI. Review the golden diff with the weight diff | Reviewer |
| Monte Carlo read as a confidence interval from real data | Medium | High | Draws are labeled simulated. Ranges are the low/high in the YAML | Person who presents the number |
| Spreadsheet formulas drift from Python | Medium | Medium | CSV holds the Python values. XLSX formulas are documented in ADR 0005. CI does not execute Excel | Person who opens the workbook |
| Formula bug that still looks internally consistent | Low | High | The ROI gate restates the savings identity. `evalkit.roi_regression` must exit 1 | Repository owner |
| Optional HTTP adapter pointed at a live vendor during an eval | Low | Medium | `build_eval_provider` ignores `DECIDE_REAL_PROVIDER` and loads the cassette. Tests block sockets | Person running CI |
| Secret committed | Low | High | `.env` is gitignored. `secretscan` runs in CI and in pre-commit | Author of the change |

Not covered: legal review of automated refunds, customer harm from a wrong refund, insurance, staffing plans, and security of a future connector. Those belong to a real deployment, which this repo is not.
