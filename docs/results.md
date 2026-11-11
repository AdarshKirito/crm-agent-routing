# Results in detail

Every measured result, with its confidence interval, its caveats and the file it comes from. The [README](../README.md#results-in-brief) has the summary; the method is in [evaluation.md](evaluation.md).

## Summary

Held-out test set, run once after all tuning: 194 tasks per system, Gemini 3.8 Flash as every system's main
model ([`results/test_summary.md`](../results/test_summary.md)).

| | ReAct (the benchmark's agent) | ReAct + the benchmark's privacy prompt | crmroute (routed) |
|---|---|---|---|
| business tasks solved, single-turn (n=114) | 56.1% | 50.0% | 71.1% |
| business tasks solved, multi-turn (n=38) | 28.9% | 21.1% | 47.4% |
| confidential requests refused (n=42) | 0% | 59.5% | 92.9% |
| list-price cost per task (all 194) | $0.075 | $0.073 | $0.028 |

How far these numbers go:

- **Against ReAct with its privacy prompt**, the baseline that is asked to protect data, crmroute is ahead by
  +21.1 points on single-turn and +26.3 on multi-turn business tasks and +33.3 on refusals. All three 95%
  intervals exclude zero, also in the check described next.
- **Against plain ReAct, the business-task lead depends on a cap I set.** The patched harness does not send a
  request above 250K input tokens and scores the task as a failure. That ended 17 ReAct tasks (8 business
  single-turn, 3 multi-turn) and none of crmroute's. Counted as ReAct successes instead, the lead is +7.9
  points single-turn [-0.9, +17.5] and +10.5 multi-turn [-7.9, +28.9], no longer significant
  ([`results/robustness_checks.md`](../results/robustness_checks.md)). Plain ReAct refuses nothing because
  nothing asks it to.
- **crmroute's prompts were tuned on this benchmark; ReAct's were not.** Its per-task hints encode the
  benchmark's answer conventions, learned on dev tasks. With only those hints removed (an ablation run after the
  test, every task on 3.8 Flash), crmroute solved 64.0% of business single-turn and 39.5% of multi-turn tasks,
  5.3 and 10.5 points fewer than with them; the sample cannot confirm either drop
  ([`results/ablation_hints.md`](../results/ablation_hints.md)). Without the hints, crmroute is level with plain
  ReAct once ReAct's capped tasks count as successes (single-turn +0.9 [-7.0, +8.8]) and still ahead of ReAct
  with the privacy prompt (+8.8 [+0.9, +16.7]). Refusals do not use the hints and did not change.
- **The cost gap does not depend on the cap** (the capped ReAct tasks stopped early, so ReAct's cost is if
  anything understated). crmroute bounds tool results and sends 9 of 19 task types to Gemini 3.1 Flash-Lite;
  it used 76K tokens per business single-turn task against ReAct's 212K.
- **Grading:** the benchmark's graders with a local qwen3:8b model as judge and simulated user for every system,
  so these numbers compare the systems here but not with the paper's GPT-4o-graded tables.

After the test I fixed the guard's misses and measured the fixes on 620 tasks no earlier run had used: on the
188 confidential requests among them that the router had also never seen, refusals rose from 93.1% to 97.9%.
On a third org from the same benchmark family (the original CRMArena), crmroute scored 82.2% against ReAct's
75.6% at 54% lower cost per task, a difference 90 tasks cannot confirm.

Last, I added **checkable answers**: crmroute gives a business answer only when code can check it against a
receipt of the tool calls it rests on and three independent runs agree, under a release rule whose risk was
certified on a calibration split; otherwise it withholds the answer and says why. On 304 new held-out
single-turn tasks it answered 123 (40.5%), and 9 of those were wrong (7.3%; exact 95% upper bound 12.4%, above
the 10% target). All 230 evidence entries behind the released answers reproduced against the live orgs. The
same procedure certified no rule for ReAct with the privacy prompt or for a single crmroute run, so both would
withhold everything. The other 59.5% of tasks go to a person, and the 9 wrong answers were unanimous and
grounded, an error a receipt cannot show ([below](#checkable-answers-resultscheckable_answersmd)).

A second round added a **competence map**, because errors that every run shares are invisible to agreement and
receipts: the task types whose released answers were wrong more than 15% of the time in round 1's records are
withheld from the start. Calibrated anew and tested once on the benchmark's last 431 unused single-turn business
tasks, crmroute answered 194 (45.0%), and 9 of those were wrong (4.6%; exact 95% upper bound 8.0%, inside the 10%
target this time). Round 1's rule on the same runs answered 159 (36.9%), 14 of them wrong. Coverage missed its
pre-registered 50% target, and again no rule was certified for one run or for the baseline
([round 2](#round-2-a-competence-map-resultscheckable2_answersmd)).

A third round repeated the procedure on an org crmroute was not built on, the original CRMArena org's 660 unused
single-turn tasks. Certified on 327 of them and applied once to the other 333, crmroute answered 144 (43.2%),
and 7 of those were wrong (4.9%; exact 95% upper bound 8.9%), so the certificate replicated. Coverage missed 50%
again. Round 3 also tested a **convention check**: it re-runs an answer's deciding query under each reading of its
question's dates ("winter of 2023" has three) and holds the answer back when the reading the org uses gives
another answer. With readings learned from 510 earlier tasks' keys, it held back 8 of 9 wrong unanimous answers in
six task types, but also 17.1% of the right ones. On the three types pre-registered for it, it held back 3 of 4
wrong answers at a cost of 5.6% of right ones; the counts are small. Round 2's rule, applied unchanged, answered
57.7% here with 5.2% wrong (bound 8.7%) ([round 3](#round-3-a-replication-on-another-org-resultscheckable3_answersmd)).
The parts that do not depend on Salesforce are packaged as [`checkable/`](../checkable/).

The numbers are summaries in [`results/`](../results/), made from the run records by the scripts in `scripts/`;
the test, fresh, original-org, robustness and ablation summaries name their exact commands. The raw run records
are published as release assets, [run-records-2026-10-11](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-10-11)
(58 MB), for the hints ablation, [run-records-2026-10-30](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-10-30),
and for checkable answers, [run-records-2026-11-01](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-11-01)
(171 MB, the receipts included), its second round, [run-records-2026-11-01-round2](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-11-01-round2)
(149 MB), and its third, [run-records-2026-11-05-round3](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-11-05-round3)
(24 MB), so every summary can be rebuilt.

## Results on the held-out test set

The test set ran once, after all tuning: `data/test.json`, 194 tasks per system (114 business and 42
confidentiality single-turn tasks, 38 multi-turn tasks) across both CRMArena-Pro orgs. All four systems used
Vertex AI Gemini 3.8 Flash as the big model and Gemini 3.1 Flash-Lite as the small model and policy
classifier, thinking `low`, eval mode `aided`, with local `ollama_chat/qwen3:8b` as judge and simulated user.
The full table, commands and pins are in `results/test_summary.md`.

| system | business single-turn (n=114) | business multi-turn (n=38) | refusal rate (n=42) | list-price $/task (all 194) | 3.8 Flash calls per business single-turn task |
|---|---|---|---|---|---|
| 1. ReAct (the benchmark's agent) | 56.1% [46.5, 64.9] | 28.9% [15.8, 42.1] | 0.0% | 0.075 | 6.7 |
| 2. ReAct + privacy prompt | 50.0% [40.4, 58.8] | 21.1% [7.9, 34.2] | 59.5% [45.2, 73.8] | 0.073 | 6.9 |
| 3. crmroute, 3.8 Flash only | 69.3% [61.4, 77.2] | 50.0% [34.2, 65.8] | 92.9% [83.3, 100] | 0.044 | 8.0 |
| 4. crmroute, routed | 71.1% [62.3, 79.8] | 47.4% [31.6, 63.2] | 92.9% [83.3, 100] | 0.028 | 4.4 |

Paired differences on the same task ids (95% bootstrap CI; I count a difference only when the interval excludes
zero). The last column counts every baseline task that hit the 250K-token cap as a baseline success instead:

| comparison | business single-turn | business multi-turn | refusal rate | business single-turn, the baseline's capped tasks counted as successes |
|---|---|---|---|---|
| crmroute (3.8 Flash) vs ReAct | **+13.2** [+5.3, +21.9] | **+21.1** [+2.6, +39.5] | **+92.9** [+83.3, +100] | +6.1 [-3.5, +15.8] |
| crmroute (routed) vs ReAct | **+14.9** [+7.0, +22.8] | **+18.4** [+2.6, +34.2] | **+92.9** [+83.3, +100] | +7.9 [-0.9, +17.5] |
| crmroute (3.8 Flash) vs ReAct + privacy prompt | **+19.3** [+11.4, +28.1] | **+28.9** [+10.5, +47.4] | **+33.3** [+19.0, +47.6] | **+14.0** [+5.3, +23.7] |
| crmroute (routed) vs ReAct + privacy prompt | **+21.1** [+12.3, +29.8] | **+26.3** [+7.9, +42.1] | **+33.3** [+19.0, +47.6] | **+15.8** [+7.0, +25.4] |
| routed vs 3.8 Flash only | +1.8 [-3.5, +7.0] | -2.6 [-15.8, +7.9] | +0.0 | |

What the numbers say:

- The guard refused 39 of 42 confidential requests. The benchmark's agent refused none, and its privacy prompt
  managed 25 while costing 6 points of business accuracy (not significant). The 3 misses were questions about
  order quantity limits and a product exclusion rule. Dev had no request of either kind and the written policy
  did not list them, so I found them on test and left the test result as measured. The routed system's guard also
  refused one customer-facing business task (b2b/1987, multi-turn: the simulated user asked about a purchase
  "by the contact with ID 003…"), which the 3.8 Flash-only system answered. Behind the guard, the solver of
  each system declined 5 of the 16 customer-facing business tasks as confidential, 4 of them single-turn
  knowledge_qa questions; this was not counted as a false refusal until 2026-10-31 (see Limitations).
- On the same model, crmroute scored 13-15 points higher than ReAct on single-turn and 18-21 points higher on
  multi-turn business tasks, at about 40% lower cost per task with every task on 3.8 Flash. Two things qualify
  this. ReAct hit the harness's 250K-token request cap on 8 single-turn and 3 multi-turn business tasks, each
  scored as a failure; counted as ReAct successes, crmroute's lead shrinks to +6.1 to +7.9 points single-turn
  and +10.5 to +13.2 multi-turn, with intervals that include zero (`results/robustness_checks.md`). And
  crmroute's per-task hints were tuned on dev to the benchmark's answer conventions, which ReAct's stock
  prompts were not; the [hints ablation](#hints-ablation-resultsablation_hintsmd) measures what they add. Against
  ReAct with the privacy prompt, every difference stays significant either way.
- crmroute's tool results are bounded; ReAct's prompt carries every earlier observation. A business single-turn
  task took 212K tokens across all of ReAct's model calls, against 103K for crmroute on 3.8 Flash and 76K routed.
  The only ablation so far removes the per-task hints; the tool-result bound and the checker were not ablated,
  so the rest of the gap is not attributed to either.
- Routing sent 71 of 152 business tasks (47%) to Flash-Lite, cut 3.8 Flash calls per business single-turn task
  from 8.0 to 4.4 and the test run's cost from $8.59 to $5.42 (-37%). Success did not change measurably
  (+1.8 points single-turn, -2.6 multi-turn), but the multi-turn interval [-15.8, +7.9] is wide enough to hide a
  real loss.
- The test run cost $42.65 at list price ($14.52, $14.12, $8.59 and $5.42 for systems 1-4). All recorded runs
  come to about $113: $30 before the test (smoke tests, dev tuning, the final dev run, a ReAct cost probe and the
  PR-eval baseline), $42.66 for the test including one failed attempt, and $41 after it (the fresh, original-org
  and ablation runs; `results/robustness_checks.md`, from the task records and the per-call logs). These are
  list-price estimates from usage metadata, not invoices.
- To check the judge, I compared it with labels for 40 blind test items, made against the reference answers
  (drafted with AI assistance, every row reviewed by me; `evals/human_labels_test.csv`). The qwen3:8b judge
  agreed on 39 of 40, Cohen's κ = 0.95 (target ≥ 0.7). The one disagreement is a multi-turn answer that ranks two
  states before concluding with the right one; the grader extracts every state a reply names, so it scored the
  answer wrong.

## After the test run

The test run showed 3 missed refusals. Reviewing the code afterwards, I found two failure paths that had not
triggered on test: a customer request with no usable verdict from the policy classifier was allowed unless the
router's vote said confidential (and a classifier error crashed the request), and a checker that could not
verify any Id answered "None", which claims that no record matches. I fixed all three and measured the fixes on
tasks no earlier step had used, so the test set stayed untouched. There was also no evidence beyond the two
CRMArena-Pro orgs; the original-CRMArena run below is the first step there. A hints ablation reran system 3
on the test tasks without its per-task hints, to measure what that dev tuning adds. Last, checkable answers
changed what crmroute does with an answer it cannot back up, built and measured on 912 tasks no earlier step
had used; a second round, a competence map learned from those 912, was measured on the benchmark's last 841
unused tasks.

### Safety fixes, measured on fresh tasks (`results/fresh_summary.md`)

I wrote the fixes from the written policy and the knowledge base, not from test tasks. The confidential list now
covers the whole quote-configuration rule family: it had mandatory bundles, volume discounts and competing
offers, but not the Product Quantity Limits and Product Exclusion Constraints articles both orgs hold. The
classifier now fails closed in customer sessions, and the checker says it could not verify an answer instead
of answering "None". The fixes were frozen before I read any fresh result. `data/fresh.json`, committed before
any run, holds 620 tasks per system that no tuning step or earlier run used; the measured image and the fixed
image ran the same tasks with the test run's pins.

| measure (same 620 fresh tasks) | n | measured agent | fixed agent | difference [95% CI] |
|---|---|---|---|---|
| confidential requests refused | 408 | 96.3% | 99.0% | **+2.7** [+1.2, +4.4] |
| of those, requests not in the router's example file | 188 | 93.1% | 97.9% | **+4.8** [+2.1, +8.0] |
| confidential company knowledge refused | 136 | 89.0% | 97.1% | **+8.1** [+3.7, +13.2] |
| order-limit and bought-together wording refused | 16 | 7/16 | 16/16 | +56.2 [+31.2, +81.2] |
| customer business requests refused by the guard, single- and multi-turn | 76 | 1 | 0 | |
| customer business requests the solver declined after the guard allowed them | 76 | 13 | 15 | |
| business tasks, single-turn | 174 | 64.9% | 66.7% | +1.7 [-2.9, +6.3] |
| business tasks, multi-turn | 38 | 50.0% | 55.3% | +5.3 [-5.3, +18.4] |

- The fresh tasks were new to every run, but not all of them to the router. Its example file was drawn from
  every non-test task before the fresh split existed, so 220 of the 408 confidential requests are labelled
  examples in it, and the router's predicted type reaches the policy classifier as a hint. Those 220 were
  refused 99.1% and 100% of the time; the 188 the router had not seen are the fairer measure, 93.1% → 97.9%.
  The test set has no such overlap (`results/robustness_checks.md`).
- The order-limit row is picked with a fixed regex that, on the test set, selects exactly the three missed
  requests, so it measures the targeted gap directly.
- The fail-closed classifier and the checker's abstention never triggered on these tasks (no missing verdict,
  no answer left with unverified Ids), so they are safeguards rather than score changes.
- The 4 confidential requests still answered read like customer-service questions the policy allows, and they
  were answered before the fixes too. The one guard false refusal (measured agent only) was a multi-turn task in
  which the simulated user had neither an order number nor an account name for a purchase "by the team".

### Another org from the same benchmark: the original CRMArena (`results/original_test_summary.md`)

The original CRMArena org has its own data, a smaller schema (16 objects, no opportunities, leads or quotes)
and 9 task types, all of which CRMArena-Pro also has. I left the agent's code and per-task hints unchanged and
added only the org's schema text, router examples from its non-test tasks (`scripts/add_org.py`) and a
knowledge index; scoring its tasks needed a harness fix first (`a918dc2`). Its routing table was fitted on its
own 90 dev tasks with the shipped rule (`results/original_dev_summary.md`: 3 of 9 types to Flash-Lite) and
committed before the 90 test tasks ran once.

| system (90 test tasks, Gemini 3.8 Flash) | success [95% CI] | vs ReAct [95% CI] | list-price $/task | tokens/task |
|---|---|---|---|---|
| ReAct (the benchmark's agent) | 75.6% [66.7, 84.4] | | 0.068 | 174K |
| crmroute, 3.8 Flash only | 81.1% [73.3, 88.9] | +5.6 [-3.3, +14.4] | 0.041 | 96K |
| crmroute, routed with the org's own table | 82.2% [74.4, 90.0] | +6.7 [-1.1, +14.4] | 0.031 | 84K |

- crmroute is ahead, but not significantly. The lead over ReAct shrinks from 13-15 points on CRMArena-Pro to
  6-7 here, mainly because ReAct does much better on this simpler schema (75.6% vs 56.1%), and 90 tasks cannot
  separate the two. One ReAct task hit the 250K-token cap here.
- It is 40% (3.8 Flash only) and 54% (routed) cheaper per task than ReAct.
- The routing method carried over: the org's own table sent 30 of 90 tasks to Flash-Lite and cut cost 24%
  against 3.8 Flash only, with no measurable difference in success (+1.1 [-5.6, +7.8]).
- The router was not the bottleneck. With the org's examples added it named the right task type for all 90
  requests, and built from the CRMArena-Pro examples alone it also scores 90/90 offline
  (`results/router_transfer.json`). Between the two Pro orgs, a router built from the other org's examples
  scores 0.907 (0.928-0.948 with both). These questions come from the same benchmark family, with the same
  templated task context, so this says nothing yet about a company's own phrasing.
- A routing table needs the org's own dev runs. One Pro org's dev split (median 6 tasks per type) is too small
  for the shipped rule (8 per type); with 4, a table fitted on one Pro org cut the other's dev cost by about half,
  at +1.9 and -4.8 points (intervals spanning zero; `results/routing_transfer.json`).

### Hints ablation (`results/ablation_hints.md`)

The per-task hints (25 lines over the 19 business task types in `agent/app/task_specs.py`) encode the
benchmark's answer conventions, which ReAct's prompts do not have. To measure what they add, I reran system 3
(every task on 3.8 Flash) on the 194 test tasks with `CRMROUTE_TASK_HINTS=0`, which leaves only those lines out
of the solver prompt; the task goal, answer form, general rules and checker stay. The image is the test image
with only that flag added (`deploy/hints_ablation.Dockerfile`), and the run used the test run's pins. It is the
one run after the test that reuses its tasks: it changes nothing in the agent, and nothing was changed because
of it.

| business tasks (test, 3.8 Flash) | n | ReAct | crmroute without hints | crmroute with hints | without vs with [95% CI] |
|---|---|---|---|---|---|
| single-turn | 114 | 56.1% | 64.0% | 69.3% | -5.3 [-13.2, +2.6] |
| multi-turn | 38 | 28.9% | 39.5% | 50.0% | -10.5 [-26.3, +5.3] |

- Removing the hints cost 5.3 points single-turn and 10.5 multi-turn, but neither drop is significant at this
  sample size. The largest drops are in task types whose hints spell out a definition or which policy articles
  apply (quote approval 4 to 0 of 6, sales cycle 6 to 3); lead qualification went the other way (0 to 3 of 6).
  With 6 tasks per type, these are descriptive.
- Without the hints, the single-turn lead over plain ReAct is +7.9 [+0.9, +14.9] as measured and +0.9
  [-7.0, +8.8] with ReAct's capped tasks counted as successes. So against plain ReAct, crmroute's single-turn
  lead is significant only as measured, with the cap in place; counting the capped tasks as ReAct successes, it
  is +6.1 with the hints and +0.9 without, neither significant. On multi-turn tasks, the lead without the hints
  is not significant even as measured (+10.5 [-5.3, +26.3]).
- Against ReAct with the privacy prompt, the single-turn lead without the hints stays significant either way
  (+14.0 [+7.0, +21.1] measured, +8.8 [+0.9, +16.7] best case); the multi-turn best case, +15.8 [+0.0, +31.6],
  does not exclude zero.
- Refusals do not use the hints (92.9% either way), and cost per business single-turn task barely moved ($0.0433
  without, $0.0427 with; ReAct $0.0792). The run cost $7.97 at list price.
- What stays without the hints (the tool-result bound, the checker, and the general rules and answer forms, also
  partly written from dev) was not ablated part by part.

### Checkable answers (`results/checkable_answers.md`)

crmroute gives a business answer only when the answer can be checked, and otherwise withholds it and says why,
so that a person can take the request over (method and pre-registration: `docs/checkable_answers.md`). I built
it on 152 practice tasks and fixed every choice before calibrating it on 456 more and testing it once on 304,
all CRMArena-Pro single-turn business tasks that no earlier split used (`data/checkable_*.json`). Every trial,
including the ones that failed, is in `results/checkable_notebook.md`.

1. **A receipt for every answer.** Every tool call is recorded with its SOQL or SOSL text, its status (ok,
   error, blocked by the confidentiality policy, budget used up), the row counts the Salesforce server reports
   and the result as the model saw it (`agent/app/receipts.py`). The benchmark's ReAct agent keeps every query
   and its output in its trajectory, so the same receipts are rebuilt for it.
2. **Code checks the answer against its receipt** (`agent/app/receipt_check.py`, standard library only). An
   answer cannot be shown from its receipt if it names an Id no tool result holds, rests on no tool result,
   does not parse in its task's form, or declines instead of answering. Softer flags are recorded too; three
   matter in practice: the tool budget ran out, a tool call failed, and a "None" that no empty query result
   supports.
3. **Independent runs must agree.** Each question goes to three runs: two of the routed system and one with
   every task on 3.8 Flash, which in practice disagreed with some of the mistakes the routed runs shared.
4. **Free text and judgments are never released.** Task types whose answer is free text (knowledge_qa,
   sales_insight_mining) or a BANT judgment read from call transcripts (lead_qualification) are always
   withheld: a receipt can show where such an answer's words came from, not that it is right.
5. **A release rule with a certified risk.** A family of rules fixed in advance, from "all three runs agree
   and no receipt has a flag" to looser ones. Learn-then-Test on the calibration runs (fixed-sequence testing,
   exact binomial p-values, alpha = delta = 0.10) chose the loosest rule certified to keep the share of wrong
   answers among released answers at or below 10%. The chosen rule was committed before any test result was
   read and applied unchanged.
6. **Anyone can re-run the evidence.** `scripts/recheck_receipts.py` re-runs the queries an answer rests on
   against the benchmark's orgs through simple_salesforce, not crmroute's server, and compares the live rows
   with the recorded ones.

Held-out test, 304 single-turn business tasks, rules from `results/checkable_calibration.md`:

| | answered (coverage) | wrong among answered (risk) | risk, exact 95% upper bound | right, every answer given |
|---|---|---|---|---|
| crmroute, three runs, certified rule | 123 (40.5%) | 9 (7.3%) | 12.4% | |
| crmroute, each run alone | no rule certified: 0 | | | 71.4% to 72.0% |
| ReAct + privacy prompt, one run | no rule certified: 0 | | | 54.3% |

- **The four pre-registered outcomes were met**, two of them narrowly. A rule was certified, the strictest of the
  family: all three runs agree and none of their receipts shows a used-up budget, a tool error or an unsupported
  None. Its test risk was 7.3% against a 10% target, but the exact upper bound, 12.4%, does not exclude a risk
  above 10%. It answered 40.5% of the tasks against a 40% target (36.8% on calibration). All 230 evidence
  entries behind the released answers reproduced live, against a 99% target.
- **Released answers were right 92.7% of the time**, against about 72% for one run that answers everything. The
  price is coverage: 59.5% of the tasks go to a person, every free-text and BANT task among them. The benchmark's
  score, which counts a withheld answer as a failure, falls to 37.5%.
- **The 9 wrong released answers were all unanimous and grounded.** Six name a real record where the answer
  key says there is none: five of them cite a quote-configuration rule article for a quote the key finds valid.
  A receipt shows that a record exists and was read, not that it answers the question.
- **Agreement is what certifies.** With one run, the same flags left 15.1% of crmroute's released calibration
  answers wrong and 30.1% of ReAct's, so neither certifies a rule. Calibrated on B2B tasks alone, the three runs
  released too few answers (83) to certify one for B2C.
- **Coverage is limited by sample size more than by the point estimate.** The next rule, which also releases
  answers whose agent recovered from a tool error, had 8.5% risk on calibration, but 223 answers could not
  certify it at delta 0.10. Policy-violation tasks were withheld mostly for a used-up tool budget, quote approvals
  because the runs disagreed.
- **Cost and wait:** three runs cost $0.079 per task at list price. Taking runs one at a time until the decision
  is settled gives the same decisions with 1.83 runs on average, $0.041 per task. With the three runs in
  parallel, the median wait is 20.9 s (one run: 13.6 s).
- **Outside the certified scope:** no one-run rule was certified for either system, so nothing was released on
  the 76 multi-turn test tasks. Refusals did not regress: with this image, 41 of the old test split's 42
  confidential requests were refused.

`scripts/ask.py` does the same for one question against running servers, with the certified rule
(`results/checkable_rules.json`):

```
$ python scripts/ask.py --url http://127.0.0.1:8901,http://127.0.0.1:8901,http://127.0.0.1:8902 --org b2b \
    --context "- Today's date: 2024-10-30" "What was the most frequent problem encountered with the SecureFlow \
    Suite in the third quarter of 2020? The associated product Id is 01tWt000006hV58IAE. Return only the issue Id ..."
task type (router): top_issue_identification  |  answer form: id  |  rule: agree>=3, no budget/none_without_empty/errors, ...
  run 1: 'a03Wt00000JqvNUIAZ'  flags: none  (5.6 s, $0.0026)
  run 2: 'a03Wt00000JqvNUIAZ'  flags: none  (6.1 s, $0.0024)
  run 3: 'a03Wt00000JqvNUIAZ'  flags: none  (12.1 s, $0.0105)

ANSWER: a03Wt00000JqvNUIAZ
Evidence (re-run with scripts/recheck_receipts.py, or paste the queries into any SOQL client):
  [1] soql_query: {"query": "SELECT IssueId__c, COUNT(Id) FROM Case WHERE OrderItemId__r.Product2Id = '01tWt000006hV58IAE'
      AND CreatedDate >= 2020-07-01T00:00:00Z AND CreatedDate <= 2020-09-30T23:59:59Z GROUP BY IssueId__c
      ORDER BY COUNT(Id) DESC LIMIT 1"}  -> 1 rows
```

A lead-qualification question asked the same way is withheld ("answers of form 'bant' cannot be checked against
record fields. Hand this request to a person."). The practice, calibration, test and refusal runs cost $145.77
at list price (`results/robustness_checks.md`, section 4); the live re-check makes no model calls.

#### Round 2: a competence map (`results/checkable2_answers.md`)

Round 1's records (912 tasks, three runs each) became development data once its test was done. Most wrong
answers that the looser rules released came from a few task types where every run made the same mistake, such
as sales amounts summed under another definition than the answer key's. Round 2 adds one step, fixed before any
round-2 run (pre-registration: `docs/checkable_answers.md`, "Round 2"): withhold the task types, as the router
predicts them, whose released answers were wrong more than a threshold of the time in the same system's round-1
records. A chain of six rules (a 15% and then a 20% map, three flag levels each, all three runs agreeing) was
calibrated on 410 tasks, and the widest certified rule was applied once to 431 test tasks: together, every
CRMArena-Pro single-turn business task that no earlier split or router example used (`data/checkable2_*.json`).
Same image, models and pins as round 1; every trial is in `results/checkable_notebook.md`.

Held-out test, 431 single-turn business tasks, rules from `results/checkable2_calibration.md`:

| | answered (coverage) | wrong among answered (risk) | risk, exact 95% upper bound | right, every answer given |
|---|---|---|---|---|
| crmroute, three runs, round 2's certified rule | 194 (45.0%) | 9 (4.6%) | 8.0% | |
| crmroute, three runs, round 1's certified rule | 159 (36.9%) | 14 (8.8%) | 13.4% | |
| crmroute, each run alone | no rule certified: 0 | | | 71.5% to 73.3% |
| ReAct + privacy prompt, one run | no rule certified: 0 | | | 52.9% |

- **Five of the six pre-registered outcomes were met; coverage was not.** The certified rule: all three runs
  agree, no flag required, and five types withheld, the five above 15% in round 1 (quote_approval,
  policy_violation_identification, sales_amount_understanding, invalid_config, wrong_stage_rectification). Its
  risk, 4.6%, and upper bound, 8.0%, are within the 10% target that round 1's bound missed. It answered 8.1
  points more of the tasks than round 1's rule on the same runs [+3.5, +12.8], and 45.0 more than the
  baseline, which certified nothing [+40.4, +49.7]. It answered 45.0% of the tasks against a 50% target (48.0% on
  calibration).
- **Released answers were right 95.4% of the time** (185 of 194), against 72.5% on average for one run that
  answers everything. The benchmark's score, which counts a withheld answer as a failure, is 42.9%; each run alone scored
  18.6 to 20.4 points above the baseline (every interval above zero).
- **Where the rest went:** 183 tasks were withheld by type (120 by the map, 63 free-text or BANT; the router's
  type was right on all 431) and 54 because the runs disagreed (their majority answer was right 29 times). Under
  this rule at most 57.5% of these tasks can be answered.
- **The map catches errors that repeat, not new ones.** The 9 wrong answers were unanimous: four activity_priority
  lists that hold every Id of the key plus one to three more, two regions, two agents for transfer counts and one
  routed case. activity_priority was wrong in 3 of 35 releases in round 1 (8.6%), below the line, and in 4 of 14
  here.
- **Evidence:** 419 of the 420 entries behind released answers reproduced live. The other is a `SELECT COUNT()`
  that the re-check script compared wrongly: simple_salesforce's `query_all` reports how many rows it fetched,
  none for a bare count, instead of the count. With the server's count it reproduces, as do the other three bare
  counts behind released answers; the script now compares the count (round 1's released evidence had none).
- **Cost and wait:** three runs cost $0.080 per task at list price, $0.045 with runs taken one at a time until
  the decision is settled (1.63 runs on average). With the three runs in parallel the median wait was 33.5 s
  (one run: 18.8 s); this round's latency includes a ten-minute Vertex AI slowdown and model calls that took
  several minutes. Round 2's runs cost $121.91 at list price (`results/robustness_checks.md`, section 4).

#### Round 3: a replication on another org (`results/checkable3_answers.md`)

Round 3 ran round 2's agent, unchanged, on the original CRMArena org's 660 single-turn tasks that no earlier
split, development run or router example used. They were halved at random within each type: 327 for calibration
and 333 for test (`data/checkable3_*.json`). Everything was fixed before any fresh task ran:

- the chain of 15 rules, built from a development run on the org's 510 used tasks;
- the pinned readings, `data/conventions_original.yaml`;
- the outcomes, stop rules and audit (pre-registration: `docs/checkable3_plan.md`).

The convention check had failed its own go/no-go checks, on the CRMArena-Pro records and then on that development
run: it held back too many right answers. So it became a secondary hypothesis on the three types where its cost was
low. The development log, `docs/checkable3_devlog.md`, has every check, including the failures.

Held-out test, 333 single-turn tasks, rules from `results/checkable3_calibration.md`:

| | answered (coverage) | wrong among answered (risk) | risk, exact 95% upper bound | right, every answer given |
|---|---|---|---|---|
| crmroute, three runs, round 3's certified rule | 144 (43.2%) | 7 (4.9%) | 8.9% | |
| the same rule with the convention check on its three types (not certified) | 142 (42.6%) | 5 (3.5%) | 7.3% | |
| crmroute, three runs, round 2's certified rule applied unchanged | 192 (57.7%) | 10 (5.2%) | 8.7% | |
| crmroute, each run alone | | | | 73.0% to 79.0% |
| ReAct (plain prompt), its certified rule | 58 (17.4%) | 0 (0.0%) | 5.0% | 69.4% |

- **The certificate replicated; coverage did not reach its target.** A rule certified on the calibration half.
  On the test half it released 144 answers with 7 wrong, and the bound, 8.9%, is inside the 10% target. All 230
  evidence entries behind the released answers reproduced live. It answered 43.2% of the tasks against a 50%
  target. The rule needs all three runs to agree, and withholds handle_time, policy_violation_identification and
  transfer_count, as well as free-text answers.
- **The convention check catches wrong answers whose question has more than one reading, at a cost.** On
  unanimous answers in six types it held back 8 of 9 wrong answers and 25 of 146 right ones (17.1%). Asking every
  reading instead held back 32.2% of the right ones, and asking none held back 18.5% while catching 5 of the 9.
  On its three pre-registered types it held back 3 of 4 wrong answers and 4 of 71 right ones (one-sided Fisher
  p = 0.002).
  - Example: all three runs read "winter 2020" as December 2019 to February 2020. The org's pinned reading is
    December 2020 to February 2021, under which the key's answer follows.
  - Its chance control was 11.8%, above the 10% bar the go/no-go checks set, so part of what it catches is luck.
- **Round 2's rule transferred.** Certified on CRMArena-Pro, it withholds only one type that exists here. Applied
  unchanged, it answered 57.7% of the test half with 5.2% wrong, and 59.1% of all 660 tasks with 5.9% wrong
  (bound 8.3%). On the calibration half alone its bound was 10.2%, so on that half it would not have certified.
  - Round 3's own chain never reached that rule. Its fixed sequence stopped one step earlier, at a stricter flag
    level (p = 0.37).
- **Keys no reading reproduces.** For 6 of 218 checked tasks, no run and no reading gives the key's answer: three
  transfer counts, two handle times and one case routing.
- **The blinded audit was not conducted.** No reader with the domain knowledge was available. Instead, the author
  reviewed 13 answers, not blind, by recomputing them from the org's records under each reading
  (`results/checkable3_review.md`). Those were the 7 wrong released answers and the 6 keys above.
  - **Released answers.** Of the 7 wrong ones, 4 are wrong under every reading. For the other 3, the question has
    two defensible readings: a "winter of 2020" asked before that winter began, twice, and "closures in November"
    counted by creation date. Counting those 3 as right gives 4 wrong of 144 (2.8%, bound 6.2%). The certificate
    stays stated against the key.
  - **Keys.** Five of the six depart from their task's stated policy or follow an unstated convention. The same
    recomputation over all the org's transfer-count and handle-time tasks finds two systematic patterns. Keys count
    every agent who held a case where the policy says the first agent: 13 of 13 tasks where the two readings
    differ. And "fewest transfers" ranks only agents with a transfer. Both are reported upstream as CRMArena
    [#31](https://github.com/SalesforceAIResearch/CRMArena/issues/31).
- **Cost:** three runs cost $0.091 per task at list price. With the three runs in parallel, the median wait was
  39.7 s. Round 3 cost $113.57 at list price: $14.24 for development, $48.00 for calibration and $51.33 for test.

Secondary outcomes are in `results/checkable3_secondary.md`.

## Design decisions and what did not work

| Decision | Why | Evidence |
|---|---|---|
| **BM25 is the default knowledge search, not hybrid + rerank** (the original plan) | Policy queries are line-item text ("CloudLink Designer: quantity 20, discount 30%"); lexical matching suits them, and the MS MARCO cross-encoder was trained on natural questions | recall@5 0.827 for BM25 vs 0.735 hybrid and 0.349 hybrid + rerank on constructed dev queries (table below) |
| **Task type from a nearest-neighbour vote, not an LLM call** | No added latency or cost per request; the label picks the model and the task hints, and is one hint to the policy classifier | 93.8% on the 194 test requests, helped by the benchmark's templated task context |
| **Bounded tool results** | ReAct's history grows with every observation until requests exceed the context budget | 103K vs 212K tokens per business task, and 0 vs 17 tasks ended by the 250K cap; this choice was not ablated, so the gap is not this choice alone |
| **One pinned model per role, retries on the same model** | A run that silently falls back to another model is not a measurement of either | provider fallback exists for the local demo only |
| **Routing judged on cost, not on accuracy** | About 11 dev tasks per type cannot show per-type accuracy differences | -37% cost; success differences +1.8 and -2.6 points, not significant |
| **Guard misses found on test fixed from the policy, measured on fresh tasks** | Fixing them against the test tasks would be tuning on test; the gap was a missing rule family, visible in the knowledge base | 3 of 42 misses on test; on 188 fresh requests new to the router, 93.1% -> 97.9% refused |
| **The policy classifier fails closed** | A safety check that allows requests when it fails protects nothing in exactly those cases | no fallback in 620 fresh tasks, so no accuracy cost |
| **Each org brings its own router examples and routing table** | Request wording and model strengths differ per org; its own dev runs decide which types go to the small model | original CRMArena org: router 90/90, own table -24% cost with no measurable loss |

<details>
<summary><b>Knowledge search: recall@5 on 381 dev queries</b> (<code>results/retrieval_dev.json</code>)</summary>

The queries come from dev-side tasks (all tasks not in `test.json`) whose answer is a knowledge-article Id.
Policy violations use the case's subject and description as the query; quote approval and invalid configuration
use the quote's name and line items.

| system | recall@5 [95% CI] | MRR@10 | invalid_config (153) | policy_violation (75) | quote_approval (153) |
|---|---|---|---|---|---|
| **BM25 (`Qdrant/bm25`, default)** | **0.827 [0.79, 0.87]** | 0.52 | 0.935 | 0.973 | 0.647 |
| hybrid, RRF (bge-small + BM25) | 0.735 [0.69, 0.78] | 0.48 | 0.882 | 0.987 | 0.464 |
| hybrid, DBSF | 0.719 [0.67, 0.76] | 0.49 | 0.876 | 1.000 | 0.425 |
| dense (`BAAI/bge-small-en-v1.5`) | 0.567 [0.52, 0.62] | 0.40 | 0.732 | 1.000 | 0.190 |
| hybrid + rerank (`ms-marco-MiniLM-L-6-v2`) | 0.349 [0.30, 0.40] | 0.30 | 0.366 | 1.000 | 0.013 |
| Salesforce SOSL (the MCP server's tool) | 0.244 [0.20, 0.29] | 0.22 | 0.150 | 0.933 | 0.000 |

A re-run on 2026-10-11 reproduced every row exactly except SOSL (`results/retrieval_dev_rerun_2026-10-11.json`).
The SOSL row was measured before the server got its 16K-character response cap; with the cap, some five-article
answers go over it and return an error, and SOSL scores 0.226 [0.19, 0.27]. With the cap lifted it matches the
table again. The agent's measured runs used the BM25 search, not SOSL.

The agent writes its own queries, so rerun this on the queries it actually sends before changing the default.
Every mode is switchable (`HYBRID_SEARCH_MODE`). knowledge_qa is not in this table: its answers are free text,
and the "silver" article labels I built by word overlap were wrong in 6 of 6 spot checks, so I excluded them.
knowledge_qa is scored end to end by the benchmark's F1 instead. Reproduce with `scripts/build_retrieval_set.py`,
then `scripts/eval_retrieval.py --sosl-url http://127.0.0.1:3333/mcp`.

</details>

<details>
<summary><b>Task-type router: accuracy on the 194 test requests</b> (<code>results/router_test.json</code>)</summary>

The router takes a similarity-weighted vote over the 15 nearest of 1,760 labelled example requests. The examples
come only from non-test tasks and are embedded with bge-small; there are no LLM calls. Its input is the request
plus the task context the benchmark supplies, such as "## Handle Time Policy ..." or "Today's date: ...", which
is templated per task type.

| input | accuracy |
|---|---|
| request + task context | **93.8%** (every error is a confidentiality request, which has no task context) |
| task context only (worst case: a vague first message in multi-turn) | 84.5% |

The router's label picks the model and the per-task hints. In customer sessions it is also passed to the policy
classifier as one hint among others, so refusals do depend on it in part. The test set contains no router
example; the fresh set does (see [After the test run](#after-the-test-run)).

</details>

<details>
<summary><b>Published baselines, recomputed from CRMArena's released B2B single-turn runs</b> (<code>results/published_b2b_single_turn.md</code>)</summary>

| model | business tasks success [95% CI] (n=1900) | confidentiality refusal rate (n=240) | cost/task (lower bound) |
|---|---|---|---|
| o1 | 45.8% [43.6, 48.0] | 0.4% (1 of 240) | ≥ $0.3808 |
| gpt-4o | 27.1% [25.1, 28.9] | 0.0% | ≥ $0.0566 |
| gpt-4o-mini | 20.2% [18.4, 22.1] | 0.0% | ≥ $0.0045 |

The benchmark's agent (without its privacy prompt) almost never refuses confidential requests, which is the gap
the guard targets. Success = reward 1; fuzzy tasks count as a success at token F1 ≥ 0.5. These come from the
released files, not from the paper's tables, and used GPT-4o as judge, so they are not comparable with the runs
above. The released files reuse task ids across task types, so records are keyed by type and id; an earlier
version of this table keyed them by id alone and lost 200 of the 2,140 records per model (reported upstream as
[CRMArena #30](https://github.com/SalesforceAIResearch/CRMArena/issues/30)).

</details>

<details>
<summary><b>Earlier free-tier pilot</b> (2026-09-29, superseded)</summary>

Before the Vertex project was available, the same agent ran on free tiers only (Gemini 3.1 Flash-Lite on the AI Studio key as the big model, local qwen3:8b as the small one, Groq gpt-oss-20b as policy classifier) on a 44-task dev subset (`results/dev_small_summary.md`: 63.2% vs 7.9% on business tasks). The 50-task test subset was stopped by the 500-requests/day Flash-Lite quota and is superseded by the run above. The provider smoke test from that pilot (`results/provider_smoke_2026-09-29.jsonl`, three dev tasks per model) found integration problems that I then fixed: Groq rejected a JSON response format next to tools and replayed reasoning content, small models wrote tool calls as text, a 200-row SOQL result flooded the context (now capped by the 16K-character budget and the 10-call limit), and the policy classifier's reply leaked into the solver's conversation.

</details>
