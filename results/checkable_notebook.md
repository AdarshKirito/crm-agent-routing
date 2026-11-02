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

- ReAct with the privacy prompt, one run on the same tasks (`runs/checkable_practice/react`, receipts
  rebuilt from its trajectories, router types from crmroute's run 1): 53.9% right. Through the same
  procedure its strictest one-run rule released 90 of 152 answers and 29 were wrong (32.2%); with fewer
  flags required, 110 with 39 wrong and 119 with 41 wrong. Its receipt flags separate right from wrong
  answers far less than crmroute's agreement does, so in practice no rule of its family comes near 10%.

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

## Calibration and test runs (launched 2026-10-31)

- Baseline (ReAct with the privacy prompt): calibration 456 of 456 and test 380 of 380 tasks, no API
  errors, as eight parallel streams launched at 933d75e (pre-registration part 1).
- crmroute: three calibration and three test streams launched at f414d36 and aced050 (pre-registration
  part 2; aced050 only adds `data/checkable_refusal_check.json`), image 658df1a6bc7f.
- `scripts/checkable_report.py` (19d7afc) runs the pre-registered analysis. Since the pre-registration,
  `scripts/release_eval.py` changed in two places only: it loads one mode at a time and records which run's
  answer was released. The rules, the flags (`agent/app/receipt_check.py`, unchanged) and the
  Learn-then-Test code are as pre-registered (`git diff 933d75e 19d7afc -- scripts/release_eval.py`).
- A dry run of both stages on the practice runs (in-sample, not a result) found the strictest rule
  withholding monthly_trend_analysis answers that all three runs got right: nearly every one of their
  receipts holds a SOQL error the agent recovered from. The next rule of the family allows recovered errors.
- Calibration run 1 stopped after its B2B half: on b2b/2062 Vertex AI rejected a request with 400
  INVALID_ARGUMENT ("Function call is missing a thought_signature", on the solver's `set_model_response`
  call), the server answered 500 and the runner exits when an org has an unfinished task, so B2C had not
  started. It was resumed with the same pins (the harness redoes tasks that ended in an error): from a git
  worktree at its manifest commit f414d36 whose files hash to the manifest's source digest, so the
  manifest check accepted it.
- Test run 1 stopped the same way, on the same Vertex AI error, at b2b/2130 (multi-turn), before its B2C
  parts; resumed the same way from a worktree at its manifest commit aced050. The same error ended b2c/1108
  (multi-turn) later in that run, also redone by resuming: 3 of about 2,400 crmroute sessions in these runs,
  all routed, 2 of them multi-turn.
- The host slept from about 00:47 to 10:52 on 2026-11-01 (Windows power events; a 10-hour gap in every
  stream's call log). Test runs 2 and 3 had finished before it. On waking, each container's first Vertex AI
  request failed with 401 UNAUTHENTICATED (the access token had expired; later requests refreshed it): 4
  tasks ended in an error. Earlier (00:20), calibration run 2 lost its connection to its container while
  fetching one session's state (b2c/1189). All 5 are redone by resuming. The tasks in flight at the sleep
  were the ones that failed on waking, so no recorded latency spans it (the longest single-turn test
  session took 201 s). A keep-awake
  request (SetThreadExecutionState, no settings changed) held the host awake for the rest of the runs.
- The live re-check of the test runs (`runs/checkable_test/recheck.json`) ran once all test runs had finished
  and before the rules were committed; its output was not opened until after that commit.

## Calibration and test results (2026-11-01)

- Calibration (`results/checkable_calibration.md`, committed in 0016481 before any test output was
  opened): only crmroute's three runs certified a rule, the strictest of the family. 168 of 456 answered,
  10 wrong (6.0%), p = 0.045. The next rule, which allows tool errors the agent recovered from, had 19
  wrong among 223 (8.5%, p = 0.27): below 10% as measured, but 223 answers cannot certify it at delta 0.10.
  ReAct with the privacy prompt (30.1% wrong under its strictest rule), crmroute's first run alone (15.1%)
  and the B2B-only calibration (7.2% of 83 answers, p = 0.26) certified nothing, so they withhold
  everything on test.
- Test (`results/checkable_answers.md`): 123 of 304 answered (40.5%), 9 wrong (7.3%, exact 95% upper
  bound 12.4%). The four primary outcomes are met, coverage narrowly (36.8% on calibration). All 230
  evidence entries behind released answers reproduced live.
- The 9 wrong released answers: 6 name a real record where the answer key says None (5 invalid_config,
  each a quote-configuration rule article, 3 of them Mandatory Bundles for Quotes, for a quote the key
  finds valid; 1 activity_priority), 2 give the same
  wrong stage (wrong_stage_rectification), 1 a wrong state. All three runs agreed on each, and each is
  grounded: the receipt shows the record exists and was read, not that it answers the question. The
  checks cannot see this kind of error.
- Why Id-form task types released little (counted after the fact, descriptive): quote_approval because
  the runs disagree (13 of 16 tasks), policy_violation_identification because the tool budget ran out (15
  of 16), sales_amount_understanding and monthly_trend_analysis because of recovered tool errors (11 and
  9 of 16).
- Free-text and BANT task types (knowledge_qa, sales_insight_mining, lead_qualification) are never
  released, by design. Multi-turn: neither system has a certified one-run rule, so nothing is released.
- Each run alone, with every answer given: 72.0%, 71.7% and 71.4% right against ReAct with the privacy
  prompt's 54.3%. Released answers were 92.7% right; the price is the 59.5% of tasks handed to a person.
- Adaptive repeats (runs taken one at a time until the decision is settled) make the same decisions with
  1.83 runs per task: $0.0410 per task at list price, against $0.0787 for all three runs.

## The ask demo with the certified rule (2026-11-01)

`scripts/ask.py` with the committed rule, against two new containers of the measured image (routed on port
8901 for runs 1 and 2, every task on 3.8 Flash on 8902 for run 3; call logs in `runs/ask_demo`), on the two
practice questions of the first demo:

- b2b/310 (top_issue_identification): all three runs answered a03Wt00000JqvNUIAZ, the reference, with no
  flag; released with the one SOQL query it rests on. Slowest run 12.1 s, $0.0155 for the three.
- b2b/2 (lead_qualification): the routed runs answered None with no empty result behind it, the 3.8 Flash
  run "Timeline"; withheld as a BANT judgment and handed off. Slowest run 27.0 s, $0.0534.

## Round 2: a competence map (2026-11-01)

Round 1's records (912 tasks, three runs each) became development data once its test was done.

- Where the looser rules' wrong answers came from (two of three runs agreeing, recovered tool errors allowed:
  64 wrong of 565 released): sales_amount_understanding 15 of 42 (every run summed order lines by order
  date, where the key evidently uses another definition), invalid_config 10 of 46 (a quote-configuration
  rule article cited for a quote the key finds valid), wrong_stage_rectification 8 of 39, activity_priority
  7 of 37. Every run shares these mistakes, so neither agreement nor receipts can see them.
- A competence map: withhold the predicted task types whose released answers were wrong more than a
  threshold of the time before. Scored on each round-1 split with the types chosen on the other two, at
  20% it took the three-run system from 38.6% coverage and 6.0% wrong (round 1's rule) to 54.4% and 6.2%;
  crmroute's first run alone reached 35.3% at 5.3% (15% map) and ReAct with the privacy prompt 20.7% at
  5.3%.
- An LLM cross-check of each answer against its evidence was considered and left out: the answers it would
  have to rescue beyond all three runs agreeing were wrong 57% of the time (24 of 42).
- Only 841 business single-turn tasks were still unused once every earlier split and router example is
  excluded (414 B2B, 427 B2C; 13 to 26 per org and type); an earlier estimate of 1,585 per org did not hold.
  All of them went into round 2: 410 calibration, 431 test (`data/checkable2_*.json`, aeff067).
- Pre-registration (3a76368, before any round-2 run): the chain of six rules (15% then 20% map, three flag
  levels, all runs agreeing), the widest certified rule chosen, six primary outcomes including an upper bound
  at most 10% and coverage at least 50%. Same image and pins as round 1; the baseline runs again.
- Launched 2026-11-01 15:35 from 3a76368: three crmroute runs and the baseline on both splits, ten streams;
  Vertex AI now billed to the user's second billing account (01BA45-0BFE37-3DE10E, free-trial credit, a
  $200 cap for this round set by the user).
- `scripts/checkable2_report.py`, committed after the launch and before any round-2 record was read, was
  dry-run on round-1 data (in-sample, a code check only).
- From about 15:38 to 15:48, every Vertex AI call to 3.8 Flash in every stream took 30 to 210 s instead of
  about 2 s (no errors, no rate-limit waits; one crmroute task took 653 s). It recovered by itself. Round-2
  latency figures include that window. The baseline's 250K-token cap ended some ReAct tasks as before
  (scored as its failures, as in every earlier run).
- Round 2's manifests pin the harness patch as 499226b9, round 1's as e3a9aaae: switching branches rewrote
  the patch file's line endings in the working tree. Its content is unchanged (both hash to e3a9aaae with
  carriage returns removed; `git diff f414d36 -- patches/` is empty).
- At about 16:37 the baseline's two B2B streams (about 0.3 tasks a minute, so about ten more hours) were stopped
  after 30 and 29 tasks and their unfinished tasks split three ways (`runs/checkable2_splits/*_b2b_p*.json`),
  run as six streams from a worktree at 3a76368 with the same pins (`react_p1..p3`). The report reads the
  baseline's run as `react` plus `react_p1..p3`; no task is in two of them. Slow model calls set the pace:
  most take a few seconds, a few take 2 to 6 minutes, and those few hold about half of each stream's time.
  The 3.8 Flash calibration run timed out on b2b/417 and test run 1 lost its connection on b2b/588, so both
  stop after B2B and are resumed.
- At about 17:20 the baseline's two B2C streams (about 0.65 tasks a minute) were split the same way after
  68 and 81 tasks: their unfinished tasks run as `react_p4..p6` from the same worktree and pins.
- At about 17:26 the 3.8 Flash runs' B2C work was shared out the same way: both runs stop after B2B
  (b2b/417 timed out, b2b/916 ended on MAX_TOKENS), so 3/5 of their B2C tasks started at once in a parallel
  stream (`f1x`) from the same worktree and pins; the other 2/5 run in `f1` after the B2B redo. The report
  reads each such run as both directories together.
- The first redo of b2b/417 was refused by the harness, as it should be: it was launched as a B2B-only
  stream, whose configuration fingerprint differs from the run's, and the harness ties each results file to
  its run's fingerprint ("Checkpoint configuration changed"; no task ran; it left a
  `manifest_full_b2b-single.json`). The redo then ran with the run's original configuration (both orgs):
  it redoes the B2B task, and its B2C step cannot start, because B2C part A's stream already holds that
  results file under its own fingerprint. So no task can run twice.
- More errors redone by resuming with each run's own configuration: dropped connections on b2c/1857
  (calibration 3.8 Flash part B) and b2c/824 (calibration routed run 2), a timeout on b2c/874 (test 3.8
  Flash part B); the 3.8 Flash test run's B2B half ended with three (b2b/916 MAX_TOKENS, b2b/1473 and
  b2b/2027 timed out after model calls of 2 to 6 minutes), all redone after its B2C part A had claimed the
  B2C file.
- Every calibration run complete (19:42): 410 of 410 tasks each, no duplicate across a run's directories,
  no errored record.

## Round 2: calibration (2026-11-01, `results/checkable2_calibration.md`, e7f8342)

- crmroute, three runs: the first five rules of the chain were certified; the sixth (20% map, no flag
  required: 216 of 410 answered, 16 wrong, 7.4%, p = 0.12) was not. The widest certified rule, chosen: all
  three runs agree, the 15% map (invalid_config, policy_violation_identification, quote_approval,
  sales_amount_understanding, wrong_stage_rectification withheld), no flag required: 197 of 410 answered
  (48.0%), 13 wrong (6.6%), p = 0.065.
- crmroute's first run alone and the baseline certified nothing: their strictest rules had 9 wrong of 119
  (7.6%, p = 0.24) and 6 wrong of 77 (7.8%, p = 0.34), too few answers to show a risk below 10%.
- Calibration coverage, 48.0%, is below the 50% that outcome 4 asks of the test split.

## Round 2: test (2026-11-01, `results/checkable2_answers.md`, 2316751)

- Errors redone on the test runs by resuming each with its run's configuration: b2c/608 (dropped connection) and
  b2c/883 in routed run 1, b2c/1406 (timed out) in the 3.8 Flash run's part A. b2c/883 hit the harness's 900 s
  limit three times and finished on the fourth attempt (11 model calls, about 500 s). On every attempt its first
  3.8 Flash call took 2 to 8 minutes and some later ones as long, also in the 3.8 Flash run (which finished it in
  about 835 s), while the run's median first call took 2 s; the limit is fixed in the pinned harness patch, so a
  resume with every pin unchanged was the only redo. Round 2 redid 11 tasks in all (3 calibration, 8 test; 13
  failed attempts, kept in the records).
- Every test run complete (21:37): 431 of 431 tasks each, no duplicate across a run's directories, no errored
  record; the baseline's 250K-token cap ended 20 of its tasks (scored as its failures).
- `scripts/checkable2_report.py` took the 3.8 Flash run's standard score from `f1` alone, which would have missed
  the 132 B2C tasks in `f1x`; fixed before the test stage was run (4bbd030) and checked on the calibration split.
- Live re-check (6 min 50 s, 2,037 live queries, no model calls): 2,511 of 2,513 entries matched. Behind released
  answers, 419 of 420 reproduced. The other, b2b/171's `SELECT COUNT()` (a released, right answer), recorded a count
  of 1 and re-checked as 0. That was the re-check script's mistake: it runs every SOQL query through
  simple_salesforce's `query_all`, whose totalSize counts the rows it fetched, and a bare COUNT() returns none. Run
  with `query()`, the count is 1, as recorded (the case exists, created 2024-05-02). Released answers rest on four
  bare COUNT() queries in round 2: b2b/171 and three recorded 0 (b2c/2075 twice, b2c/2101), which the script could
  not have found different; all four reproduce with the server's count. Round 1's 230 released entries had none.
  Fixed in bdec661, after the test results were committed; the committed results keep the pre-registered
  script's 419 of 420.
- Results (crmroute, three runs, the rule chosen on calibration): 194 of 431 answered (45.0%), 9 wrong (4.6%,
  exact 95% upper bound 8.0%). Outcomes 1, 2, 3, 5 and 6 met; 4 (coverage at least 50%) missed. Round 1's rule on
  the same runs: 159 answered (36.9%), 14 wrong (8.8%, bound 13.4%); coverage difference +8.1 points [+3.5,
  +12.8]. On calibration the chosen rule had answered 48.0%, 6.6% of them wrong.
- Where coverage went: 183 tasks withheld by type (120 by the map's five types, 63 free-text or BANT; the router's
  type was right on all 431), 54 because the runs disagreed (47 with two runs agreeing, 7 with none; the majority
  answer was right 29 times), none for a failed check among unanimous runs. At most 248 tasks (57.5%) can be
  released under this rule.
- The 9 wrong released answers, all unanimous: four activity_priority lists that hold every Id of the key plus one
  to three more (b2b/254, b2c/208, 220, 282), two best_region_identification (b2b/1110 TX where the key says MO,
  b2c/1159 IL where it says None), two transfer_count (b2b/1195 another agent, b2c/1275 none where the key names
  one) and one case_routing (b2b/1500, another agent). activity_priority was wrong in 3 of 35 round-1 releases
  under this rule (8.6%), below the 15% line, and in 4 of 14 here: the map withholds what went wrong before, not
  new errors.
- crmroute's first run alone and the baseline certified nothing on calibration, so they release nothing. Standard
  score of each run: crmroute 71.5%, 73.3% and 72.9%, ReAct + privacy 52.9% (+18.6 to +20.4 points, every interval
  above zero).
- Cost and wait: $0.0804 per task for three runs, $0.0445 with adaptive repeats (1.63 runs). One run p50 18.8 s,
  three in parallel 33.5 s (p95 299 s); this round's latency includes the 15:38 to 15:48 slowdown and the slow
  calls above. Round 2's model calls cost $121.91 at list price (843a96e), of the $200 cap.
- Rebuilt from the records to be published (round 1's published archive plus round 2's redacted copy): the four
  round-2 results files, and round 1's four with this branch's scripts, match byte for byte.
