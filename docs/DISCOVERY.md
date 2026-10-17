# Discovery

Ten questions. Each one fills an input. The answer changes the design, not just a cell.

1. **How many items arrive per day, and on how many days a month?**  
   Fills `volume_per_day` and `working_days_per_month` (or `volume_per_month` if the work is not daily). If the volume is tiny, fixed cost dominates and break-even may be out of reach. The tornado on the refund sketch says volume is one of the largest NPV swings.

2. **How many minutes does one item take today, end to end, including waiting on a person?**  
   Fills `manual_minutes_per_item`. If the clock time is mostly waiting, do not book it as labor. If the true touch time is half of what you guessed, savings shrink in a straight line.

3. **What is the loaded cost of an hour, not the nominal wage?**  
   Fills `loaded_cost_per_hour`. Benefits, tools and a lead's time belong here if they scale with the hour. A low loaded cost makes the personal weekly-report case fail, which is why that pessimistic scenario never pays back.

4. **What share of manual items are wrong, and what does one wrong item cost?**  
   Fills `manual_error_rate` and `cost_of_error`. If errors are cheap, quality is not the reason to automate. If they are expensive, a small drop in the error rate can matter more than the minutes.

5. **What residual error rate will you accept after the agent and the review policy?**  
   Fills `agent_error_rate`. This is a policy choice. It is subtracted in quality-adjusted savings. Setting it to zero hides the risk. This repo will not invent a measured accuracy.

6. **What fraction of items must a person still open, and how many minutes is that open?**  
   Fills `review_rate` and `review_minutes`. If the answer is "all of them, for as long as the old task", the agent does not pay. The weekly example sets review rate to 1 on purpose. The refund pessimistic set raises review rate to 0.85 and the case never pays back.

7. **How many tokens does one production item use, and what price are you willing to assume?**  
   Fills `input_tokens`, `output_tokens` and the two illustrative prices per million. Those prices are [EST], not a vendor page. A measured 23-case eval bill is already recorded in `assumptions/measured_eval_run_cost.yaml` (2026-10-17, commit `c1efdfd`) and is not one of these fields. Splitting that bill by 23 is [EST] and is not applied. A per-item override is a different file. See `docs/REPLACE_THE_ASSUMPTIONS.md`.

8. **What is the one-time cost to put it in, and what is the fixed cost every month after that?**  
   Fills `implementation_cost` and `monthly_run_cost`. The fixed cost is charged in full during the ramp (ADR 0001). If the team forgets platform and on-call, payback looks shorter than the desk will live.

9. **How many months until the desk actually uses it on every item, and who can stop the pilot?**  
   Fills `adoption_ramp_months`. The "who can stop it" answer is governance, not a cell: that person is the approver. The model does not approve. A long ramp delays payback even when steady-state savings look fine (base payback on the refund sketch is 17.08 months, not implementation divided by the steady month).

10. **What discount rate and horizon does finance use?**  
    Fills `discount_rate_annual`. The horizon in these files is 36 months, a model setting, not a measured life. A higher discount rate cuts NPV and does not change undiscounted payback. If finance wants five years, change `horizon_months` knowingly; do not stretch the story in a slide.

If a question has no answer, leave the parameter as [EST] and say so. Do not borrow a number from a blog and drop the tag.
