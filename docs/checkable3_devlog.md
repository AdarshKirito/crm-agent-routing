# Checkable answers, round 3: development log

Round 3 tests one addition to checkable answers: an answer is released only if it stays the same under
every declared reading of the conventions its question leaves open (which year "winter of 2023" belongs
to, whether "the past three quarters" is rolling or calendar, which date puts a case in a period). Each
reading is executed by rewriting the run's own recorded queries and re-running them read-only on the
live org, and the release rule is certified with Learn-then-Test as in rounds 1 and 2. The agent itself
does not change: everything new reads receipts after the runs.

This page is the development log. Nothing on it is a result. No round-3 task (the original CRMArena
org's 660 never-used single-turn tasks) has been run. The pre-registration will be
`docs/checkable3_plan.md`, written after the checks below.

## What was seen before this log

The planning research (2026-11-03) ran exploratory scripts on crmroute's CRMArena-Pro run records from
rounds 1 and 2. They were in-sample and outside the repo:

- A loose derivation check (an answer counts as derived if some query of the run, with or without the
  question's period applied, yields it) cut three-run unanimous errors in the six types below from 18 to 9
  of 471 tasks (by true task type), and withheld 28 right answers.
- In b2b/1110 ("winter of 2023"), the receipt rows give TX, the agent's answer, for December 2022 to
  February 2023, and MO, the key, for December 2023 to February 2024.

These numbers were known when the thresholds below were set. Every check below is recomputed with
versioned code. The engine is written while reading receipts from these same records, so C1 to C7 are
optimistic. C8 and the development run on the original org are the first checks on another org.

## Definitions

- **Records.** crmroute's three runs (routed runs 1 and 2, and the run on 3.8 Flash), read as in
  `scripts/checkable2_report.py`, on the five CRMArena-Pro checkable splits: round 1 practice,
  calibration and test, and round 2 calibration and test. Business single-turn tasks only. Every one of
  these tasks is already used.
- **The six types.** best_region_identification, handle_time, transfer_count, monthly_trend_analysis,
  top_issue_identification and case_routing: the types the original org shares with CRMArena-Pro whose
  answer is computed from query rows. A task belongs to the population by the router's predicted type,
  which is what a release rule may use. Counts by true type are reported beside.
- **Checkable answer.** A run answer whose claim (`receipt_check.parse_claim`, in the type's answer form)
  is Ids, None or a value.
- **Unanimous.** All three runs give checkable answers, and the same one (`receipt_check.same_answer`).
- **Derivation.** Code that computes a type's answer from query rows (`agent/app/derivation.py`). It reads
  the task context's policy (for example, whether the minimum-case filter counts transferred cases) and
  its tie rule. Where the context gives no tie rule, ties are a convention slot (below).
- **Deciding query.** Of a run's successful SOQL queries to which the derivation applies, the last one
  whose derivation reproduces the run's answer when re-run live without its LIMIT, with every row fetched.
  If none does, it is the last query to which the derivation applies.
- **Readings.** The convention slots below, declared before any check is computed. A run's readings are
  the combinations of the readings of the slots its question triggers. The run's own reading is its
  recorded query.

  | Slot | Readings | Triggered by |
  |---|---|---|
  | Season months | Meteorological: winter December to February, spring March to May, summer June to August, fall September to November (the benchmark's `get_period`); quarter-aligned: winter January to March, spring April to June, summer July to September, fall October to December | A season name |
  | Season year | "Winter (of) Y" is December Y to February Y+1 (`get_period`) or December Y-1 to February Y | "Winter" with a year, meteorological months |
  | Past N quarters | Rolling 3N months back from today; the N completed calendar quarters before the current one (SOQL `LAST_N_QUARTERS`) | "past/last N quarters" |
  | Past N months or years | Rolling back from today; the N completed calendar months or years before the current one (SOQL `LAST_N_MONTHS`, `LAST_N_YEARS`) | "past/last N months/years" |
  | Rolling end | Today's date counted; not counted | Any rolling window |
  | Date field | A case is in the period by CreatedDate; by ClosedDate | best_region_identification and handle_time with a period |
  | Ties | None on a tie; the tied value with the smallest Id or name | A derivation whose top value is shared, where the context gives no tie rule |

  "Today" is the task context's "Today's date". Windows are half-open: they start at 00:00 UTC on the
  first day and end before 00:00 UTC on the day after the last.
- **Gate levels**, for one run:
  - Own: the derivation over the deciding query, re-run live, reproduces the answer. On a tie the context
    does not settle, either tie reading counts.
  - Allowed: own holds, and the deciding query, rewritten for each allowed reading and re-run live, gives
    that same answer under every one of them.
  - Declared: the same as allowed, over every declared reading.

  A run whose check cannot be completed is unchecked: it has no applicable query, or its window does not
  parse, or a rewrite or a re-run fails. A task passes the gate when no run of its majority group fails and
  at least one passes. Otherwise its answer is withheld.
- **Allowed readings on CRMArena-Pro (cross-fitted).**
  - A run supports a reading when some combination containing that reading reproduces the key.
  - A run contradicts a reading when no combination containing it reproduces the key, but a combination
    with another reading of the same slot does.
  - A reading is excluded when no run supports it and at least one run contradicts it. If every reading of
    a slot would be excluded, none is. A reading is pinned when runs of at least three tasks support it and
    none contradicts it. Everything not excluded is allowed.
  - Round-2 tasks are judged by readings learned from round-1 tasks, and round-1 tasks by readings learned
    from round 2, so no task's own key sets the readings it is judged by.

## Go/no-go checks, fixed before any is computed

The thresholds are the planning report's proposals, adopted unchanged when the owner approved the build on
2026-11-03. All checks cost no model money; they make read-only queries only.

| Check | Population | Measure | GO if |
|---|---|---|---|
| C1 Rewrite coverage | Checkable run answers in the six types | Share whose check completes at the declared level | At least 90% |
| C2 Strict derivation | The same | Share passing the own level; the share of those passes whose deciding query's live rows hold a single group is reported | At least 85% |
| C3 Chance control | Each of those run answers, paired with the same run of the next task of its predicted type (sorted order, cyclic), pairs with the same answer left out | Share where the own level passes for the answer on the other task's receipt and question | At most 10% |
| C4 Catch | Unanimous tasks in the six types whose answer is wrong (18 by true type in the planning count) | Share withheld at the allowed level | At least 40% |
| C5 Cost | Unanimous tasks in the six types whose answer is right (453 by true type in the planning count) | Share withheld at the allowed level | At most 8% |
| C6 Added information | Unanimous wrong tasks that pass the own level | Number withheld at the allowed level (b2b/1110 is expected to be one) | At least 2 |
| C7 Rescue | Tasks in the six types whose runs disagree | Share where the key is among the answers the declared readings give; share where it is among the runs' answers | Reported only |
| C8 Portability | ReAct's checkable answers in the six types (by crmroute's routed prediction) on the original org's 90 test tasks, receipts rebuilt by `react_receipt` | C1's measure, on that org | At least 85% |
| C9 Readiness | All three orgs log in with the benchmark's published credentials; each org's remaining daily API requests (REST limits resource) cover the planned re-runs; the round-2 checkable image holds the original org's knowledge index; the split script writes an original-org split | Pass or fail | All pass |

## Decision, due Friday 2026-11-13

- **GO** if C1 to C5, C8 and C9 pass.
- If C4 and C5 pass but C6 fails, it is still GO, with a narrower headline. The gain is then arithmetic,
  which has precedent, and the convention readings stay a pre-registered arm.
- If C1 or C2 fails overall, the gate is limited to the types that pass both on their own, and C4 to C6 are
  recomputed on those types. Both computations are reported, and the decision is taken on the restricted
  one.
- **NO-GO** if C4 or C5 fails. Round 3 then runs as a replication on the original org, with the derivation
  gate as a pre-registered arm, round 2's frozen rule applied unchanged as a transfer check, and the blinded
  audit. The convention gate becomes a secondary analysis, and the failed check is reported.
- A failed C9 item is fixed and re-checked before any paid run. It does not change the decision.

Thresholds and the decision rule do not change after this commit. Any change to a definition is logged
below with its date and reason, and with the values under both definitions.

## Log

- 2026-11-03: definitions, catalog slots, thresholds and the decision rule committed. Nothing has been
  computed with versioned code yet.
- 2026-11-03, before any check is computed. The code makes these definitions concrete:
  - **Deciding query.** A query whose live re-run fails, or whose derivation ties where the context settles
    ties (case routing), cannot be the deciding query. If no query reproduces the answer, the deciding query
    is the last one that derives one.
  - **Handle time.** Handle time leaves out the transferred cases that the run's own CaseHistory__c queries
    show, re-run live.
  - **Date field.** Types without a date-field slot put cases in a period by CreatedDate, and transfers by
    the CaseHistory__c row's CreatedDate.
  - **Fixed periods.** A question naming a month or a quarter triggers no window slot. Its single reading is
    that period's window, so the check still re-runs the deciding query on exactly that window. A question
    with no period has no readings.
  - **Ties.** Case routing's tie rule (product expertise, then workload) is not computed, so a tie there
    leaves the run unchecked.
  - **Not added to catalog v0.** Development surfaced one more candidate slot, kept out so the checks use
    catalog v0 as committed. b2b/1201's key suggests that "lowest transfer count" counts only agents with at
    least one transfer. It is a candidate for the original org's used-key tests (step 6).
- 2026-11-03, the checks, computed once (`results/checkable3_gonogo.md`):
  - **Runs.** Code caa02dd and deb90d3. The Pro pass ran 14:17-14:30 with 7,615 distinct live queries, 84
    of them first fetched while testing the code on six tasks. The original-org pass ran 14:16-14:17 with
    158 queries.

  | Check | Value | Result |
  |---|---|---|
  | C1 Rewrite coverage | 1,648 of 1,671 (98.6%) | pass |
  | C2 Strict derivation | 1,399 of 1,671 (83.7%); 495 of the passes over one group | fail |
  | C3 Chance control | 163 of 1,461 (11.2%) | fail |
  | C4 Catch | 18 of 18 (100%) | pass |
  | C5 Cost | 137 of 453 (30.2%) | fail |
  | C6 Added information | 6 | pass |
  | C7 Rescue | key among the readings' answers in 78 of 86 disagreeing tasks; among the runs' answers in 75 of 86 | reported |
  | C8 Portability | 36 of 51 (70.6%) | fail |
  | C9 Readiness | logins, API allowance, knowledge index, split script | pass |

  - **C9 details.** CRMArena rotated the original org's login on 2026-11-03 (its README, 521c126). The
    local `vendor/CRMArena/.env` was updated from it, and the org's instance is the one earlier runs used.
    The Pro orgs allow 441,450 API requests a day. The original org's limits resource is disabled; its
    response header shows 441,430 a day. The round-2 image 658df1a6bc7f holds `knowledge_original`, and
    `make_checkable_splits.py --round3` writes the split (5054d71).
  - **Restricted check.** C2 failed overall, so the gate was limited to best_region_identification,
    case_routing and top_issue_identification. There C4 is 9 of 9, C5 is 49 of 248 (19.8%) and C6 is 2.
  - **Decision: NO-GO.** C5 fails, both overall and restricted. By the rule above, round 3 runs as a
    replication on the original org. The derivation gate becomes a pre-registered arm, round 2's frozen rule
    is applied unchanged as a transfer check, and the blinded audit follows. The convention gate becomes a
    secondary analysis.
  - **What the numbers show.**
    - The gate held back every unanimous wrong answer, and also 137 right ones.
    - Of those 137, 76 fail the own level (39 in monthly_trend_analysis). The other 61 change under a reading
      the keys never use, most often ClosedDate as the date field, calendar months or quarter-aligned
      seasons.
    - The exclusion rule removed no reading, because each one had at least one supporting run by
      coincidence. Pinning picked out the benchmark's conventions in both rounds: rolling windows,
      meteorological seasons, December of Y and CreatedDate.
    - C8's 15 incomplete checks are all ReAct's two-step product filter: order items first, then cases by a
      literal list of their Ids. The derivation does not yet treat such a query as limited to the product.
