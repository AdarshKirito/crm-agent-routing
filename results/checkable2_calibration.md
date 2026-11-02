# Checkable answers, round 2: the certified release rules

```
python scripts/checkable2_report.py --stage calibration
```

Learn-then-Test on the round-2 calibration runs (`data/checkable2_calibration.json`), alpha 0.1, delta 0.1, over the pre-registered chain: each system's competence map is learned on its own round-1 runs only. Each table stops at the first rule that is not certified; of the certified rules, the one that answers the most calibration tasks is chosen. Committed before any round-2 test result is read.

## crmroute, three runs (two routed, one on 3.8 Flash)

410 calibration tasks, 3 run(s) each; competence maps from 912 round-1 tasks.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified | types withheld by the map |
|---|---|---|---|---|---|---|---|
| agree>=3, no budget/none_without_empty/errors, withhold 2 types wrong >15% before, withhold bant/text answers | 144 of 410 (35.1%) | 9 (6.2%) | 9.7% | 32.9% | 0.0805 | yes | invalid_config, policy_violation_identification |
| agree>=3, no budget/none_without_empty, withhold 3 types wrong >15% before, withhold bant/text answers | 177 of 410 (43.2%) | 10 (5.6%) | 8.6% | 40.7% | 0.0287 | yes | invalid_config, policy_violation_identification, sales_amount_understanding |
| agree>=3, withhold 5 types wrong >15% before, withhold bant/text answers | 197 of 410 (48.0%) | 13 (6.6%) | 9.5% | 44.9% | 0.0645 | yes | invalid_config, policy_violation_identification, quote_approval, sales_amount_understanding, wrong_stage_rectification |
| agree>=3, no budget/none_without_empty/errors, withhold 2 types wrong >20% before, withhold bant/text answers | 144 of 410 (35.1%) | 9 (6.2%) | 9.7% | 32.9% | 0.0805 | yes | invalid_config, policy_violation_identification |
| agree>=3, no budget/none_without_empty, withhold 3 types wrong >20% before, withhold bant/text answers | 177 of 410 (43.2%) | 10 (5.6%) | 8.6% | 40.7% | 0.0287 | yes | invalid_config, policy_violation_identification, sales_amount_understanding |
| agree>=3, withhold 4 types wrong >20% before, withhold bant/text answers | 216 of 410 (52.7%) | 16 (7.4%) | 10.2% | 48.8% | 0.1210 | no | invalid_config, policy_violation_identification, quote_approval, sales_amount_understanding |

Chosen: **agree>=3, withhold 5 types wrong >15% before, withhold bant/text answers**

## crmroute, first routed run alone

410 calibration tasks, 1 run(s) each; competence maps from 912 round-1 tasks.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified | types withheld by the map |
|---|---|---|---|---|---|---|---|
| agree>=1, no budget/none_without_empty/errors, withhold 8 types wrong >15% before, withhold bant/text answers | 119 of 410 (29.0%) | 9 (7.6%) | 11.7% | 26.8% | 0.2375 | no | activity_priority, best_region_identification, invalid_config, policy_violation_identification, quote_approval, sales_amount_understanding, sales_cycle_understanding, wrong_stage_rectification |

Chosen: **none (every answer is withheld)**

## ReAct with the privacy prompt, one run

410 calibration tasks, 1 run(s) each; competence maps from 912 round-1 tasks.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified | types withheld by the map |
|---|---|---|---|---|---|---|---|
| agree>=1, no budget/none_without_empty/errors, withhold 12 types wrong >15% before, withhold bant/text answers | 77 of 410 (18.8%) | 6 (7.8%) | 13.3% | 17.3% | 0.3396 | no | activity_priority, best_region_identification, conversion_rate_comprehension, handle_time, invalid_config, monthly_trend_analysis, policy_violation_identification, quote_approval, sales_amount_understanding, sales_cycle_understanding, transfer_count, wrong_stage_rectification |

Chosen: **none (every answer is withheld)**

