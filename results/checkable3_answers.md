# Checkable answers, round 3: results on the held-out test half

```
python scripts/checkable3_report.py --stage test
```

The rule certified on the calibration half (`results/checkable3_calibration.md`), applied unchanged to the 333 test tasks. Risk is the share of wrong answers among the answers given, with its exact one-sided 95% upper bound.

| rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|
| all runs agree, withhold 3 types, withhold bant/text answers | 144 of 333 (43.2%) | 7 (4.9%) | 8.9% | 41.1% |

## Pre-registered primary outcomes (crmroute, three runs)

1. A rule of the chain certified on the calibration half: **yes, all runs agree, withhold 3 types, withhold bant/text answers**.
2. Wrong among released test answers at most 10%, and its exact one-sided 95% upper bound at most 10%: **yes** (7 of 144, 4.9%; bound 8.9%).
4. Evidence behind released answers reproduced live (at least 99%): **yes**: 230 of 230 entries reproduced exactly, 0 SOSL searches ranked differently (their answer Ids are checked separately); released Id answers with an Id missing live: 0.
5. At least 50% of the 333 test tasks answered: **no** (43.2%).

(P3, the gate's mechanism outcome, became a secondary analysis when G2 failed: below.)

## The pinned gate, secondary analysis (test half)

| types | unanimous held back: wrong of all | passed: wrong of all | one-sided Fisher p |
|---|---|---|---|
| its three types | 3 of 7 | 1 of 68 | 0.0020 |
| all six | 8 of 33 | 1 of 122 | 0.0000 |

| rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score | runs per task |
|---|---|---|---|---|---|
| runs 1-3 agree on best_region_identification/case_routing/transfer_count, gate pinned, withhold 3 types, withhold bant/text answers | 142 of 333 (42.6%) | 5 (3.5%) | 7.3% | 41.1% | 1.99 |
| runs 1-2 agree on best_region_identification/case_routing/transfer_count, gate pinned, withhold 3 types, withhold bant/text answers | 145 of 333 (43.5%) | 5 (3.4%) | 7.1% | 42.0% | 1.77 |
| run 1 on best_region_identification/case_routing/transfer_count, gate pinned, withhold 3 types, withhold bant/text answers | 151 of 333 (45.3%) | 7 (4.6%) | 8.5% | 43.2% | 1.55 |

## crmroute's chosen rule by true task type (test)

| task type (true) | tasks | answered | wrong among answered | right without the rule |
|---|---|---|---|---|
| best_region_identification | 37 | 23 | 2 | 25 |
| case_routing | 37 | 28 | 0 | 31 |
| handle_time | 37 | 0 | 0 | 25 |
| knowledge_qa | 38 | 0 | 0 | 32 |
| monthly_trend_analysis | 37 | 22 | 1 | 28 |
| named_entity_disambiguation | 37 | 37 | 1 | 36 |
| policy_violation_identification | 37 | 0 | 0 | 9 |
| top_issue_identification | 35 | 34 | 3 | 31 |
| transfer_count | 38 | 0 | 0 | 26 |
