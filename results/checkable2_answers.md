# Checkable answers, round 2: results on the held-out test split

```
python scripts/checkable2_report.py --stage test
```

The rules certified on the round-2 calibration runs (`results/checkable2_calibration.md`), applied unchanged to the round-2 test runs (`data/checkable2_test.json`, 431 single-turn business tasks, the benchmark's last unused ones). Risk is the share of wrong answers among the answers given, with its exact one-sided 95% upper bound (Clopper-Pearson); the standard score counts a withheld answer as a failure, as the benchmark does.

## Released answers, round-2 test

| system | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|---|
| crmroute, three runs (two routed, one on 3.8 Flash) | agree>=3, withhold 5 types wrong >15% before, withhold bant/text answers | 194 of 431 (45.0%) | 9 (4.6%) | 8.0% | 42.9% |
| crmroute, first routed run alone | withhold_all | 0 of 431 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |
| ReAct with the privacy prompt, one run | withhold_all | 0 of 431 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |
| crmroute, three runs, round 1's certified rule | agree>=3, no budget/none_without_empty/errors, withhold bant/text answers | 159 of 431 (36.9%) | 14 (8.8%) | 13.4% | 33.6% |

## Pre-registered primary outcomes (crmroute, three runs)

1. A rule of the chain certified on the round-2 calibration split: **yes, agree>=3, withhold 5 types wrong >15% before, withhold bant/text answers**.
2. Wrong among released test answers at most 10%: **yes** (9 of 194, 4.6%).
3. Its exact one-sided 95% upper bound at most 10%: **yes** (8.0%).
4. At least 50% of the 431 test tasks answered: **no** (45.0%).
5. Evidence behind released answers reproduced live (at least 99%): **yes**: 419 of 420 entries reproduced exactly, 0 SOSL searches ranked differently (their answer Ids are checked separately); released Id answers with an Id missing live: 0.
6. More test tasks answered than round 1's rule on the same runs and than the baseline under its own round-2 rule, both paired intervals above zero: **yes** (round 1's rule +8.1 [+3.5, +12.8] points, baseline +45.0 [+40.4, +49.7] points).

## Paired differences on the same 431 test tasks (crmroute three runs, chosen rule, minus ...)

| other | coverage, points [95% CI] | standard score, points [95% CI] |
|---|---|---|
| round 1's certified rule, same runs | +8.1 [+3.5, +12.8] | +9.3 [+4.9, +13.7] |
| ReAct + privacy, its own round-2 rule | +45.0 [+40.4, +49.7] | +42.9 [+38.3, +47.6] |
| crmroute's first run alone, its own round-2 rule | +45.0 [+40.4, +49.7] | +42.9 [+38.3, +47.6] |

## Standard benchmark score of each run (every answer given), round-2 test

| run | right | vs ReAct + privacy, points [95% CI] |
|---|---|---|
| crmroute routed run 1 | 308 of 431 (71.5%) | +18.6 [+13.9, +23.2] |
| crmroute routed run 2 | 316 of 431 (73.3%) | +20.4 [+16.0, +25.1] |
| crmroute 3.8 Flash run | 314 of 431 (72.9%) | +20.0 [+15.8, +24.4] |
| ReAct + privacy | 228 of 431 (52.9%) |  |

## Repeats, latency and cost (crmroute, three runs)

| measure | value |
|---|---|
| tasks | 431 |
| mean success of one run | 72.5% |
| pass^3 (every run right) | 272 (63.1%) |
| runs giving the majority answer = 3 | 315 tasks |
| runs giving the majority answer = 2 | 98 tasks |
| runs giving the majority answer = 1 | 18 tasks |
| latency of one run, p50 / p95 | 18.8 s / 139.3 s |
| latency with the 3 runs in parallel (slowest run), p50 / p95 | 33.5 s / 299.2 s |
| list-price cost per task, all 3 runs | $0.0804 |

With adaptive repeats (runs taken one at a time, routed runs first, until the decision is settled; the same decisions; a withheld task type stops after the router) the chosen rule needs 1.63 solver runs per task: $0.0445 per task instead of $0.0804.

## crmroute's chosen rule by true task type (test)

| task type (true) | tasks | answered | wrong among answered | right without the rule |
|---|---|---|---|---|
| activity_priority | 24 | 14 | 4 | 12 |
| best_region_identification | 24 | 18 | 2 | 18 |
| case_routing | 24 | 22 | 1 | 21 |
| conversion_rate_comprehension | 23 | 17 | 0 | 22 |
| handle_time | 21 | 17 | 0 | 20 |
| invalid_config | 23 | 0 | 0 | 13 |
| knowledge_qa | 14 | 0 | 0 | 0 |
| lead_qualification | 23 | 0 | 0 | 14 |
| lead_routing | 23 | 22 | 0 | 22 |
| monthly_trend_analysis | 22 | 19 | 0 | 20 |
| named_entity_disambiguation | 16 | 13 | 0 | 14 |
| policy_violation_identification | 24 | 0 | 0 | 20 |
| quote_approval | 25 | 0 | 0 | 17 |
| sales_amount_understanding | 24 | 0 | 0 | 15 |
| sales_cycle_understanding | 24 | 16 | 0 | 19 |
| sales_insight_mining | 26 | 0 | 0 | 5 |
| top_issue_identification | 24 | 24 | 0 | 24 |
| transfer_count | 23 | 12 | 2 | 14 |
| wrong_stage_rectification | 24 | 0 | 0 | 18 |
