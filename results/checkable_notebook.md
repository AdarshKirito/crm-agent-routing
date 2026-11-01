# Checkable answers: lab notebook

Every trial of the checkable-answers work, in order, including the ones that did not help. Practice runs
use `data/checkable_practice.json` only; the calibration and test splits stay unused until the method is
frozen and pre-registered in `docs/checkable_answers.md`. Costs are list price.

## 2026-10-31: receipts and a smoke test

- Receipts added to the agent (`agent/app/receipts.py`) and copied into task records by the harness patch.
  Image `crmroute:checkable` built from commit 6f1f9d4.
- Smoke test on two practice tasks (b2b/310 top_issue_identification, b2b/707 knowledge_qa): both records
  carry their receipts. The knowledge question's receipt shows what the old records could not: 10 tool
  calls, the budget used up, and an answer ("Data Integration Toolkit") whose reference ("ChipLink
  Integrator") appears in no knowledge article and in nothing the agent retrieved.
- `scripts/recheck_receipts.py` re-ran the entries both answers rest on against the live org with
  simple_salesforce: 8 of 8 reproduced. On an earlier ReAct run (`runs/dev_react_probe`, 38 tasks) 47 of
  48 entries reproduced exactly; the exception is a 250-row SOSL search whose rows differ between calls
  (Salesforce ranks SOSL results), and all 20 Id answers' Ids came back live.

## Practice round 1

crmroute routed three times (`runs/checkable_practice/r1..r3`) and ReAct with the privacy prompt once
(`runs/checkable_practice/react`), 152 single-turn business tasks, image `crmroute:checkable`
(7ce729a5441f, built from 6f1f9d4), launched at d0153b5 (6f1f9d4 plus the release script), with the test
run's model and judge pins.

- Each run alone: 71.1%, 70.4% and 71.1% of the 152 tasks right; no API errors.
- Where the wrong answers come from (runs 1 and 3, read from the receipts): knowledge_qa 2 of 16 right and
  sales_insight_mining 5 of 16, mostly text the agent never retrieved; lead_qualification 4 of 16; and
  "saw the right record, picked another" in quote_approval (8 answers), handle_time (5) and
  activity_priority (4). case_routing, lead_routing, monthly_trend_analysis and top_issue_identification
  were right in all 16.
- Receipt flags on the first 132 answers: no flag 77% right; budget used up 33% (21 answers); a None with
  no empty result behind it 25% (8); refusal 0% (5); tool errors 67%; an Id seen only in cut-off results
  93% (not a warning sign: dropped from the rules).
- Agreement alone does not reach a 10% risk: with two runs agreeing and no budget or unsupported-None
  flag, 96 answers were released and 16 were wrong, 7 of them free-text answers (knowledge_qa,
  sales_insight_mining). A receipt cannot check a free-text answer graded by word overlap with a
  paraphrase, nor a BANT judgment over call transcripts, so those answer forms are withheld by the
  predicted type's form (`--withhold-forms text,bant`); the router predicted the type of 151 of the 152
  tasks correctly.
- Three runs, forms withheld (in-sample, practice only):

  | rule | released | wrong | risk |
  |---|---|---|---|
  | all 3 agree, no budget / unsupported None / tool errors | 62 of 152 | 3 | 4.8% |
  | all 3 agree, no budget / unsupported None | 76 | 5 | 6.6% |
  | 2 agree, no budget / unsupported None / tool errors | 79 | 6 | 7.6% |
  | all 3 agree, no flag required | 106 | 13 | 12.3% |
  | 2 agree, no budget / unsupported None | 94 | 10 | 10.6% |

  The question-anchor flags (an unused question Id, a period without a date filter) withheld right answers
  without lowering the risk (7.8% for all 3 agreeing), so they stay recorded but out of the rules.
- The 5 wrong answers the second rule released were consistent across all three runs and are errors of
  meaning, not of evidence: a stage change where the key says the stage is right, a partly matching set of
  tasks, a policy violation where the key says none (invalid_config, whose labels a 2026 preprint finds
  unrecoverable from the visible inputs), and two sales-amount answers that used another period or amount
  definition than the key. Four of the five are task types the routed system sends to Flash-Lite, so a
  3.8 Flash run may disagree on them: practice round 3 tests that.
- Live re-check of all three runs (`scripts/recheck_receipts.py`, simple_salesforce, not crmroute's
  server): the first pass reproduced 809 of the 845 entries the 456 answers rest on. The 36 others were
  differences of the re-check, not of the data: integers written as 25 by the server and 25.0 by the Python
  client, knowledge results the confidentiality filter had thinned (now compared as subsets, like cut
  results), record fetches by SOQL over every field (now by Id), API 59.0 lacking four User fields the
  server's 62.0 has, and LastViewedDate/LastReferencedDate, which Salesforce updates whenever a record is
  viewed. After those fixes all 845 entries reproduce and every Id of the 237 Id answers comes back live.
- A knowledge_qa false refusal, read from its receipt: the only article naming the product ("Mandatory
  Bundles for Quotes") is internal under the sensitive-data map, so the filter withheld it and its note
  told the solver to refuse; the reference answer is in no article either. Kept as is: on the fresh run 24
  of 408 confidential requests were refused by the solver after the guard allowed them, so the same
  instruction is a second line of defence. A refused business question counts as withheld.

## Practice round 2: receipt-guided retry (did not help; off)

The checker's retry was given to answers whose receipt showed the tool budget used up or a None with no
empty result behind it, with 4 extra tool calls and feedback naming the problem
(`CRMROUTE_RECEIPT_RETRY_CALLS=4`, image 658df1a6bc7f, commit 1175af9; `runs/checkable_practice/rr1`).
Stopped after 87 of the 152 tasks, once the answer was clear, to save about $1.60:

- On the 33 tasks where a round-1 run had either flag, the retry run was right 48.5% of the time against
  57.6% for the round-1 runs; on the other 51 tasks both were right 86.3% of the time.
- It cannot help the release rule either: an answer reached after a used-up budget keeps its budget flag
  (23 budget-flagged answers against 16 per round-1 run).

The retry stays in the code, off by default (`CRMROUTE_RECEIPT_RETRY_CALLS=0`), and is not part of the
evaluated system.

## The ask command

`scripts/ask.py` against its own container (port 8099, call log `runs/ask_demo`, so no measured run's
logs mix with it), on two practice questions:

- b2b/310 (top_issue_identification): three parallel runs answered a03Wt00000JqvNUIAZ, the reference, with
  no flag; released with the one SOQL query it rests on (cases of the product, Q3 2020, grouped by issue).
  Slowest run 11.2 s, $0.0146 for the three.
- b2b/2 (lead_qualification): both runs answered None with no empty result behind it; withheld because a
  BANT judgment cannot be checked against record fields, and handed off. $0.0077.

The two questions cost $0.0223 in all.

## Pre-registration, part 1

`docs/checkable_answers.md` now fixes the method before any calibration or test run: the splits (the
calibration split raised from 8 to 12 tasks per org and type first, for the power to certify), the
withheld answer forms, the rule family and its order, alpha = delta = 0.10, the primary outcomes and what is
reported either way. The baseline's protocol is complete with it, so its calibration and test runs start
after this commit, as eight parallel streams (each split in two halves by `scripts/split_halves.py`, one
stream per half and org). crmroute's run composition is fixed after practice round 3, before any crmroute
calibration or test run.

## Practice round 3: one run on 3.8 Flash for every task (cross-model agreement)

crmroute with every task on 3.8 Flash (system 3) once on the practice tasks (`runs/checkable_practice/f1`,
image 658df1a6bc7f, commit 1175af9): 109 of 152 right (71.7%), no API errors.

- Of the 76 answers the three routed runs agreed on cleanly (all three, no budget or unsupported-None
  flag), the 3.8 Flash run disagreed with 2 of the 5 wrong ones (b2b/233 activity_priority, b2c/871
  sales_amount_understanding) and with 2 of the 71 right ones.
- Two routed runs plus the 3.8 Flash run, over the three ways of pairing (in-sample):

  | runs | all 3 agree, no budget / unsupported None / tool errors | all 3 agree, no budget / unsupported None |
  |---|---|---|
  | routed, routed, routed | 62 released, 3 wrong (4.8%) | 76 released, 5 wrong (6.6%) |
  | r1, r2, 3.8 Flash | 61, 2 (3.3%) | 75, 4 (5.3%) |
  | r1, r3, 3.8 Flash | 65, 3 (4.6%) | 77, 4 (5.2%) |
  | r2, r3, 3.8 Flash | 59, 2 (3.4%) | 73, 3 (4.1%) |

  At the two-of-three rules it does not help (9.9-10.0% against 7.6% for the strictest of them), since two
  routed runs can outvote it.
- Decision (pre-registration part 2): two routed runs and one 3.8 Flash run, in that order for adaptive
  repeats; list price about $0.074 per task against $0.070 for three routed runs.
