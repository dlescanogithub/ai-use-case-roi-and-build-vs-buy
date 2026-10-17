# Discovery

Two lists. The first fills the ROI file. The second fills the decision kit. Answer them with the people who will live with the choice. The tools do not ask the questions.

If a question has no answer, leave the parameter as [EST] and say so. Do not borrow a number from a blog and drop the tag.

## ROI questions

1. **How many items arrive per day, and on how many days a month?**  
   Fills `volume_per_day` and `working_days_per_month` (or `volume_per_month`). If the volume is tiny, fixed cost dominates. On the refund sketch, volume is one of the largest NPV swings.

2. **How many minutes does one item take today, excluding wait you would not save?**  
   Fills `manual_minutes_per_item`. If the true touch time is half of what you guessed, savings shrink in a straight line.

3. **What is the loaded cost of an hour, not the nominal wage?**  
   Fills `loaded_cost_per_hour`. A low loaded cost makes the personal weekly-report case fail, which is why that pessimistic scenario never pays back.

4. **What share of manual items are wrong, and what does one wrong item cost?**  
   Fills `manual_error_rate` and `cost_of_error`.

5. **What residual error rate will you accept after the agent and the review policy?**  
   Fills `agent_error_rate`. Setting it to zero hides the risk. This repo will not invent a measured accuracy.

6. **What fraction of items must a person still open, and how many minutes is that open?**  
   Fills `review_rate` and `review_minutes`. The weekly example sets review rate to 1 on purpose. The refund pessimistic set raises review rate to 0.85 and the case never pays back.

7. **How many tokens does one production item use, and what price are you willing to assume?**  
   Fills the token counts and the two illustrative prices per million. Those prices are [EST]. A measured 23-case eval bill is already recorded in `assumptions/measured_eval_run_cost.yaml` (2026-10-17, commit `c1efdfd`) and is not one of these fields. Splitting that bill by 23 is [EST] and is not applied.

8. **What is the one-time cost to put it in, and what is the fixed cost every month after that?**  
   Fills `implementation_cost` and `monthly_run_cost`. The fixed cost is charged in full during the ramp.

9. **How many months until the desk actually uses it on every item, and who can stop the pilot?**  
   Fills `adoption_ramp_months`. The "who can stop it" answer is governance, not a cell. The model does not approve. Base payback on the refund sketch is 17.08 months, not implementation divided by the steady month.

10. **What discount rate and horizon does finance use?**  
    Fills `discount_rate_annual`. The horizon in these files is 36 months. A higher discount rate cuts NPV and does not change undiscounted payback.

## Decision questions

| # | Question | If the answer goes one way | What you change |
| --- | --- | --- | --- |
| 1 | Is the decision one workflow, or a whole platform? | One workflow, such as shipment exceptions | Keep one case directory. Do not add scores from two workflows together |
| 2 | Who uses it, and about how many seats and runs? | A desk of about a dozen people | `seats` and `runs_per_year`. A tenfold volume change is the `volume_spike` scenario |
| 3 | What does a month of waiting cost? | Waiting is painful because a peak is close | Raise `time_to_value`. On the committed Bruma inputs, +0.031 on that weight flips the winner to Vendor A |
| 4 | Where must the text live, and who may train on it? | Text stays in the team's tenancy | A score on `security_compliance` and `control`, written as a rationale. The kit does not verify the claim |
| 5 | What does good look like in 90 days, and in 3 years? | 90 days is a reviewed draft; 3 years is a set the team still owns | 90 days informs `time_to_value`. 3 years informs `maintainability`, `exit_cost`, and the TCO horizon |
| 6 | Who maintains it after month six? | One person, part time | Keep `eval_ops_hours_per_year` and `review_hours_per_year` honest |
| 7 | What happens if the vendor raises the price 20%? | The renewal would be painful | Run the `price_shock` scenario |
| 8 | What is the exit? | Export is a CSV, or there is no export | Score `exit_cost` to match that story, and set the TCO `exit_cost` to the rebuild effort |
| 9 | How wrong can the build estimate be before the decision flips? | The team has overrun builds before | Read the flip list and the `build_overrun` scenario (1.5× hours) |
| 10 | Who may approve an effect such as sending a reply or changing a record? | A person on the desk sends the reply | Leave the effect outside the tool. This repo writes a Markdown file. Anything else stays design-only |

If question 10 has the answer "the agent should send it alone", stop and design the approval. Do not encode that as a higher score.

After the decision still looks worth a conversation, answer the ROI list for that option. Do not copy the decision-kit dollars into the ROI file by hand and drop the `[EST]` tag. Re-enter the numbers you will defend, with a source.
