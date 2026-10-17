# Adapt this to a real client

Short version. Do not copy the fictional numbers.

1. New private assumption file. New fictional-looking id until the client agrees the file can name them. This portfolio repo should not gain a real client name.
2. Sit the discovery questions in `docs/DISCOVERY.md` with the process owner and with finance. Write their answers into the YAML. Leave `[EST]` on anything they did not measure.
3. Follow `docs/REPLACE_THE_ASSUMPTIONS.md` for which input to replace and which question produces it. A 23-case eval bill is already on disk and is not a per-item cost. Pass `--measured-cost` only for a file whose `agent_cost_per_run` was measured for one production item. Record the command and the date in `source`. Do not type a price from a vendor page into that field.
4. Run `python -m roi_model.cli run` and read the pessimistic row before the base row.
5. A person approves showing the number. This program will not.
6. Keep the eval gate. If you change the formula, the identity check and the forced regression are how you know the gate still works.
7. Shadow first: the calculator does not move a ticket, a refund, or a call. A gate on a real system is a different project.

Out of scope here: their data, their contract, their brand, and any fee.
