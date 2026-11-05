# Checkable answers, round 3: secondary outcomes

```
vendor/CRMArena/.venv/Scripts/python scripts/checkable3_secondary.py
```

The pre-registered secondary outcomes (`docs/checkable3_plan.md`), computed once after the primary ones (`results/checkable3_answers.md`) from the same runs and committed rules. Nothing here is certified and nothing feeds back into a rule. Risk bounds are exact one-sided 95%; paired intervals are bootstrap 95% over the same tasks. S4 (readings proposed by the model) was not run, as the plan says.

## S1 and S10: the whole chain on the test half (the risk-coverage curve)

Every rule of the pre-registered chain (`results/checkable3_frozen.json`), strictest first, applied to the test half's three runs. Learn-then-Test stopped at rule 10 on the calibration half, so rules 10 to 15 were never certified; they are shown to draw the curve.

| # | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|---|
| 1 | all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | 37 of 333 (11.1%) | 1 (2.7%) | 12.2% | 10.8% |
| 2 | all runs agree, no budget/none_without_empty, withhold 4 types, withhold bant/text answers | 78 of 333 (23.4%) | 2 (2.6%) | 7.9% | 22.8% |
| 3 | all runs agree, withhold 5 types, withhold bant/text answers | 99 of 333 (29.7%) | 4 (4.0%) | 9.0% | 28.5% |
| 4 | all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | 37 of 333 (11.1%) | 1 (2.7%) | 12.2% | 10.8% |
| 5 | all runs agree, no budget/none_without_empty, withhold 4 types, withhold bant/text answers | 78 of 333 (23.4%) | 2 (2.6%) | 7.9% | 22.8% |
| 6 | all runs agree, withhold 5 types, withhold bant/text answers | 99 of 333 (29.7%) | 4 (4.0%) | 9.0% | 28.5% |
| 7 | all runs agree, no budget/none_without_empty/errors, withhold 3 types, withhold bant/text answers | 51 of 333 (15.3%) | 2 (3.9%) | 11.8% | 14.7% |
| 8 | all runs agree, no budget/none_without_empty, withhold 2 types, withhold bant/text answers | 108 of 333 (32.4%) | 4 (3.7%) | 8.3% | 31.2% |
| 9 (chosen) | all runs agree, withhold 3 types, withhold bant/text answers | 144 of 333 (43.2%) | 7 (4.9%) | 8.9% | 41.1% |
| 10 | all runs agree, no budget/none_without_empty/errors, withhold 1 types, withhold bant/text answers | 65 of 333 (19.5%) | 2 (3.1%) | 9.4% | 18.9% |
| 11 | all runs agree, no budget/none_without_empty, withhold 1 types, withhold bant/text answers | 117 of 333 (35.1%) | 4 (3.4%) | 7.7% | 33.9% |
| 12 | all runs agree, withhold 1 types, withhold bant/text answers | 192 of 333 (57.7%) | 10 (5.2%) | 8.7% | 54.7% |
| 13 | all runs agree, no budget/none_without_empty/errors, withhold bant/text answers | 75 of 333 (22.5%) | 8 (10.7%) | 18.4% | 20.1% |
| 14 | all runs agree, no budget/none_without_empty, withhold bant/text answers | 129 of 333 (38.7%) | 12 (9.3%) | 14.6% | 35.1% |
| 15 | all runs agree, withhold bant/text answers | 223 of 333 (67.0%) | 35 (15.7%) | 20.3% | 56.5% |

Round 2's six rules (the chain's first six; rules 4 to 6 repeat 1 to 3 because maps 15 and 20 withhold the same types) against the chosen rule, on the same test tasks:

| round 2's rule | chosen minus it: coverage, points [95% CI] | standard score, points [95% CI] |
|---|---|---|
| all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | +32.1 [+27.0, +37.2] | +30.3 [+25.5, +35.4] |
| all runs agree, no budget/none_without_empty, withhold 4 types, withhold bant/text answers | +19.8 [+15.6, +24.0] | +18.3 [+14.4, +22.5] |
| all runs agree, withhold 5 types, withhold bant/text answers | +13.5 [+9.9, +17.1] | +12.6 [+9.0, +16.2] |

## S2 and S3: gate levels on the test half's unanimous answers

The catalog declares 14 readings over 7 slots; D1's keys pin 7, leave 7 allowed and exclude 0. With nothing excluded, the allowed level equals the declared level on this org.

All six row-computed types (by predicted type):

| gate level | wrong answers held back (catch) | right answers held back (cost) | held back: wrong of all | passed: wrong of all | one-sided Fisher p |
|---|---|---|---|---|---|
| own | 5 of 9 (55.6%) | 27 of 146 (18.5%) | 5 of 32 | 4 of 123 | 0.0190 |
| pinned (the frozen conventions) | 8 of 9 (88.9%) | 25 of 146 (17.1%) | 8 of 33 | 1 of 122 | 0.0000 |
| allowed (every reading D1's keys do not exclude) | 8 of 9 (88.9%) | 47 of 146 (32.2%) | 8 of 55 | 1 of 100 | 0.0011 |
| declared (every catalog reading) | 8 of 9 (88.9%) | 47 of 146 (32.2%) | 8 of 55 | 1 of 100 | 0.0011 |

The secondary hypothesis's three types (best_region_identification, case_routing, transfer_count):

| gate level | wrong answers held back (catch) | right answers held back (cost) | held back: wrong of all | passed: wrong of all | one-sided Fisher p |
|---|---|---|---|---|---|
| own | 0 of 4 (0.0%) | 4 of 71 (5.6%) | 0 of 4 | 4 of 71 | 1.0000 |
| pinned (the frozen conventions) | 3 of 4 (75.0%) | 4 of 71 (5.6%) | 3 of 7 | 1 of 68 | 0.0020 |
| allowed (every reading D1's keys do not exclude) | 3 of 4 (75.0%) | 12 of 71 (16.9%) | 3 of 15 | 1 of 60 | 0.0236 |
| declared (every catalog reading) | 3 of 4 (75.0%) | 12 of 71 (16.9%) | 3 of 15 | 1 of 60 | 0.0236 |

The chosen rule with each gate level added on the three types (reported, not certified):

| gate | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|
| none (the chosen rule) | 144 of 333 (43.2%) | 7 (4.9%) | 8.9% | 41.1% |
| own | 144 of 333 (43.2%) | 7 (4.9%) | 8.9% | 41.1% |
| pinned | 142 of 333 (42.6%) | 5 (3.5%) | 7.3% | 41.1% |

## S5: the chance control

A run's answer, put on the same run of the next task of its predicted type, passes the own level in 67 of 568 (11.8%) pairs (test half; the go/no-go bar on the Pro records was at most 10%).

## S6: ReAct through the same chain

ReAct's rule, certified on the calibration half (`results/checkable3_calibration.md`), on the test half:

| system | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|---|
| crmroute, three runs | all runs agree, withhold 3 types, withhold bant/text answers | 144 of 333 (43.2%) | 7 (4.9%) | 8.9% | 41.1% |
| ReAct, one run | all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | 58 of 333 (17.4%) | 0 (0.0%) | 5.0% | 17.4% |

crmroute minus ReAct on the same 333 tasks: coverage +25.8 [+21.3, +30.6] points, standard score +23.7 [+19.2, +28.5] points.

Standard benchmark score of each run (every answer given, scored as the benchmark does):

| run | right | minus ReAct, points [95% CI] |
|---|---|---|
| crmroute routed run 1 | 243 of 333 (73.0%) | +3.6 [-1.5, +8.7] |
| crmroute routed run 2 | 250 of 333 (75.1%) | +5.7 [+0.6, +10.8] |
| crmroute 3.8 Flash run | 263 of 333 (79.0%) | +9.6 [+4.8, +14.1] |
| ReAct | 231 of 333 (69.4%) | |

ReAct's rule by true task type (test):

| task type (true) | tasks | answered | wrong among answered | right without the rule |
|---|---|---|---|---|
| best_region_identification | 37 | 0 | 0 | 17 |
| case_routing | 37 | 28 | 0 | 37 |
| handle_time | 37 | 0 | 0 | 22 |
| knowledge_qa | 38 | 0 | 0 | 31 |
| monthly_trend_analysis | 37 | 0 | 0 | 28 |
| named_entity_disambiguation | 37 | 30 | 0 | 36 |
| policy_violation_identification | 37 | 0 | 0 | 8 |
| top_issue_identification | 35 | 0 | 0 | 29 |
| transfer_count | 38 | 0 | 0 | 23 |

## S7: round 2's certified rule, frozen and applied unchanged

Round 2's rule (`results/checkable2_rules.json`: agree>=3, withhold 5 types wrong >15% before, withhold bant/text answers) withholds five CRMArena-Pro types; of them only policy_violation_identification exists on the original org. Both halves are fresh tasks for a rule fixed before round 3, so both are shown. Its certificate (risk at most 10%) is the question.

| tasks | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|---|
| test half | round 2's rule | 192 of 333 (57.7%) | 10 (5.2%) | 8.7% | 54.7% |
| test half | round 1's rule | 75 of 333 (22.5%) | 8 (10.7%) | 18.4% | 20.1% |
| calibration half | round 2's rule | 198 of 327 (60.6%) | 13 (6.6%) | 10.2% | 56.6% |
| calibration half | round 1's rule | 74 of 327 (22.6%) | 11 (14.9%) | 23.4% | 19.3% |
| both halves | round 2's rule | 390 of 660 (59.1%) | 23 (5.9%) | 8.3% | 55.6% |
| both halves | round 1's rule | 149 of 660 (22.6%) | 19 (12.8%) | 18.1% | 19.7% |

## S8: do the readings hold the key?

Of the 66 test tasks of the six types whose three runs disagree, the key is among the answers the declared readings and derivations give in 58 of 66 (87.9%), and among the runs' own answers in 53 of 66 (80.3%).

## S9: key-reproduction flags

Of the 218 tasks whose check produced at least one answer, 11 have a key that no derivation and no reading of any run reproduces: transfer_count 7, handle_time 2, monthly_trend_analysis 1, case_routing 1.

- **No run gives the key either** (6: 495, 759, 774, 808, 842, 887): the key may follow a convention the catalog does not declare, or be wrong.
- **Some run gives the key, the check does not** (5: 215, 806, 843, 896, 908): a gap in the derivation, not in the key.

All are listed in `results/checkable3_key_flags.json` and go to the blinded audit, which a person has to carry out; it is not done yet.

## S10: the standard report

- **Always-None baseline.** Answering "None" to every test task is right on 58 of 333 (17.4%) (the share of None keys); of the 144 answers the chosen rule released, 19 have a None key.
- **Errors per type** are in `results/checkable3_answers.md`.

Repeats, latency and cost (crmroute, three runs, test half):

| measure | value |
|---|---|
| tasks | 333 |
| mean success of one run | 75.7% |
| pass^3 (every run right) | 219 (65.8%) |
| runs giving the majority answer = 3 | 260 tasks |
| runs giving the majority answer = 2 | 61 tasks |
| runs giving the majority answer = 1 | 12 tasks |
| latency of one run, p50 / p95 | 24.3 s / 106.2 s |
| latency with the 3 runs in parallel (slowest run), p50 / p95 | 39.7 s / 193.3 s |
| list-price cost per task, all 3 runs | $0.0912 |

Under the chosen rule a deployment runs no solver on a withheld type, so it makes 1.99 solver runs per task. ReAct's one run costs $0.0629 per task at list price.
