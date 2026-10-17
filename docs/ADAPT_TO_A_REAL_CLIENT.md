# Adapt this to a real client

Keep the math. Replace the fiction before anyone treats an ADR or an NPV as a decision about a real organisation. Do not copy the fictional numbers.

1. New private files. New case id. Do not copy Bruma Freight, Cedro Records, or Puerto Gris Parcel Co. forward as if they were the client. This portfolio repo should not gain a real client name or a real employer name.
2. Sit both discovery lists in [DISCOVERY.md](DISCOVERY.md) with the process owner and with finance. Write their answers into the YAML. Leave `[EST]` on anything they did not measure.
3. Follow [REPLACE_THE_ASSUMPTIONS.md](REPLACE_THE_ASSUMPTIONS.md) for which input to replace. A 23-case eval bill is already on disk and is not a per-item cost. Pass `--measured-cost` only for a file whose `agent_cost_per_run` was measured for one production item. Record the command and the date. Do not type a price from a vendor page into that field.
4. For a public price page used in the TCO file, set `estimate: false`, the official `https://` URL, and the access date. The loader rejects anything else that claims to be real.
5. Run the decision report and read the disagreement between the weighted winner and the cheapest operating total before you read the score.
6. Run `python3 -m roi_and_build_vs_buy roi run` and read the pessimistic row before the base row.
7. A person approves showing the number and, separately, accepts the ADR by changing its status. This program will not.
8. Set a golden winner only after the decision owner has read that disagreement. Updating `evals/golden/decisions.json` is part of the same reviewed change.
9. Keep both eval gates, including the fixture that flips the Bruma winner if the weights are tampered with, and the fixture that injects a wrong savings formula. `evalkit` checks the calculators. It does not score an assistant.
10. Shadow first: the calculator does not move a ticket, a refund, a call, or a contract. A gate on a real system is a different project.
11. Leave scraping, procurement, and the questionnaire as follow-on work unless the engagement explicitly includes them. The questionnaire starts as [security-questionnaire-checklist.md](security-questionnaire-checklist.md), filled by a person.

Cost of the default path stays 0 USD of API spend. Leave `DECIDE_REAL_PROVIDER` and `ROI_ENABLE_REAL_PROVIDER` off unless a quote feed is explicitly in scope, and do not point CI at it.

Out of scope here: their data, their contract, their brand, and any fee.
