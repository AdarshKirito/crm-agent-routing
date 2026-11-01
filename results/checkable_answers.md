# Checkable answers: results on the held-out test split

```
python scripts/checkable_report.py --stage test
```

The rules certified on the calibration runs (`results/checkable_calibration.md`), applied unchanged to the test runs of `data/checkable_test.json` (304 single-turn business tasks, 76 multi-turn). Risk is the share of wrong answers among the answers given; its upper bound is exact (Clopper-Pearson, 95%). The standard score counts a withheld answer as a failure, as the benchmark does.

## Released answers, single-turn test tasks

| system | certified rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|---|
| crmroute, three runs (two routed, one on 3.8 Flash) | agree>=3, no budget/none_without_empty/errors, withhold bant/text answers | 123 of 304 (40.5%) | 9 (7.3%) | 12.4% | 37.5% |
| ReAct with the privacy prompt, one run | withhold_all | 0 of 304 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |
| crmroute, first routed run alone | withhold_all | 0 of 304 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |
| crmroute, three runs, calibrated on B2B only and applied to B2C | withhold_all | 0 of 152 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |

## Pre-registered primary outcomes (crmroute, three runs)

1. A rule certified on the calibration split: **yes, agree>=3, no budget/none_without_empty/errors, withhold bant/text answers**.
2. Risk on the test split at most 10%: **yes** (7.3%, 95% upper bound 12.4%).
3. At least 40% of the 304 single-turn test tasks answered: **yes** (40.5%).
4. Evidence behind released answers reproduced live (at least 99%): **yes**: 230 of 230 entries reproduced exactly, 0 SOSL searches ranked differently (their answer Ids are checked separately); released Id answers with an Id missing live: 0.

## crmroute against the baseline, paired on the same 304 tasks

| comparison | coverage, points [95% CI] | standard score, points [95% CI] |
|---|---|---|
| three runs vs ReAct + privacy | +40.5 [+35.2, +46.1] | +37.5 [+32.2, +43.1] |
| first run alone vs ReAct + privacy | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| three runs vs first run alone | +40.5 [+35.2, +46.1] | +37.5 [+32.2, +43.1] |

## Standard benchmark score of each run (every answer given), single-turn test tasks

| run | right | vs ReAct + privacy, points [95% CI] |
|---|---|---|
| crmroute routed run 1 | 219 of 304 (72.0%) | +17.8 [+12.5, +23.0] |
| crmroute routed run 2 | 218 of 304 (71.7%) | +17.4 [+12.2, +22.7] |
| crmroute 3.8 Flash run | 217 of 304 (71.4%) | +17.1 [+12.2, +22.0] |
| ReAct + privacy | 165 of 304 (54.3%) |  |

## Repeats, latency and cost (crmroute, three runs)

| measure | value |
|---|---|
| tasks | 304 |
| mean success of one run | 71.7% |
| pass^3 (every run right) | 189 (62.2%) |
| runs giving the majority answer = 3 | 228 tasks |
| runs giving the majority answer = 2 | 65 tasks |
| runs giving the majority answer = 1 | 11 tasks |
| latency of one run, p50 / p95 | 13.6 s / 58.8 s |
| latency with the 3 runs in parallel (slowest run), p50 / p95 | 20.9 s / 81.5 s |
| list-price cost per task, all 3 runs | $0.0787 |

With adaptive repeats (runs taken one at a time, routed runs first, until the decision is settled; the same decisions) the certified rule needs 1.83 runs per task: $0.0410 per task instead of $0.0787.

## crmroute's certified rule by true task type (test)

| task type (true) | tasks | answered | wrong among answered | right without the rule |
|---|---|---|---|---|
| activity_priority | 16 | 6 | 1 | 12 |
| best_region_identification | 16 | 12 | 1 | 11 |
| case_routing | 16 | 12 | 0 | 16 |
| conversion_rate_comprehension | 16 | 3 | 0 | 12 |
| handle_time | 16 | 8 | 0 | 15 |
| invalid_config | 16 | 15 | 5 | 11 |
| knowledge_qa | 16 | 0 | 0 | 1 |
| lead_qualification | 16 | 0 | 0 | 11 |
| lead_routing | 16 | 14 | 0 | 16 |
| monthly_trend_analysis | 16 | 5 | 0 | 15 |
| named_entity_disambiguation | 16 | 9 | 0 | 15 |
| policy_violation_identification | 16 | 0 | 0 | 10 |
| quote_approval | 16 | 0 | 0 | 7 |
| sales_amount_understanding | 16 | 0 | 0 | 9 |
| sales_cycle_understanding | 16 | 4 | 0 | 12 |
| sales_insight_mining | 16 | 0 | 0 | 3 |
| top_issue_identification | 16 | 13 | 0 | 15 |
| transfer_count | 16 | 7 | 0 | 14 |
| wrong_stage_rectification | 16 | 15 | 2 | 14 |

## Multi-turn test tasks (descriptive, not certified: conversations are another distribution)

| system | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |
|---|---|---|---|---|---|
| crmroute, first routed run alone | withhold_all | 0 of 76 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |
| ReAct with the privacy prompt, one run | withhold_all | 0 of 76 (0.0%) | 0 (0.0%) | 100.0% | 0.0% |

## Refusal re-check (regressions only)

The old test split's 42 confidential requests, re-run once with this image: 41 refused (97.6%); the held-out test run of 2026-10-02 refused 39 of 42 (92.9%) with the routed system.
