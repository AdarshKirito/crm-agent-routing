# Checkable answers, round 3: the certified release rules

```
python scripts/checkable3_report.py --stage calibration
```

Learn-then-Test on the round-3 calibration half (`data/checkable3_calibration.json`), alpha 0.1, delta 0.1, over the pre-registered chain (`docs/checkable3_plan.md`). Each table stops at the first rule that is not certified; of the certified rules, the one that answers the most calibration tasks is chosen. Committed before the test half launches.

## crmroute

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified |
|---|---|---|---|---|---|---|
| all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | 30 of 327 (9.2%) | 0 (0.0%) | 7.4% | 9.2% | 0.0424 | yes |
| all runs agree, no budget/none_without_empty, withhold 4 types, withhold bant/text answers | 69 of 327 (21.1%) | 0 (0.0%) | 3.3% | 21.1% | 0.0007 | yes |
| all runs agree, withhold 5 types, withhold bant/text answers | 103 of 327 (31.5%) | 1 (1.0%) | 3.7% | 31.2% | 0.0002 | yes |
| all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | 30 of 327 (9.2%) | 0 (0.0%) | 7.4% | 9.2% | 0.0424 | yes |
| all runs agree, no budget/none_without_empty, withhold 4 types, withhold bant/text answers | 69 of 327 (21.1%) | 0 (0.0%) | 3.3% | 21.1% | 0.0007 | yes |
| all runs agree, withhold 5 types, withhold bant/text answers | 103 of 327 (31.5%) | 1 (1.0%) | 3.7% | 31.2% | 0.0002 | yes |
| all runs agree, no budget/none_without_empty/errors, withhold 3 types, withhold bant/text answers | 42 of 327 (12.8%) | 0 (0.0%) | 5.3% | 12.8% | 0.0120 | yes |
| all runs agree, no budget/none_without_empty, withhold 2 types, withhold bant/text answers | 107 of 327 (32.7%) | 4 (3.7%) | 7.3% | 31.5% | 0.0145 | yes |
| all runs agree, withhold 3 types, withhold bant/text answers | 142 of 327 (43.4%) | 3 (2.1%) | 4.6% | 42.5% | 0.0002 | yes |
| all runs agree, no budget/none_without_empty/errors, withhold 1 types, withhold bant/text answers | 64 of 327 (19.6%) | 5 (7.8%) | 14.0% | 18.0% | 0.3727 | no |

Chosen: **all runs agree, withhold 3 types, withhold bant/text answers**

## baseline

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified |
|---|---|---|---|---|---|---|
| all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers | 60 of 327 (18.3%) | 1 (1.7%) | 6.3% | 18.0% | 0.0138 | yes |
| all runs agree, no budget/none_without_empty, withhold 4 types, withhold bant/text answers | 128 of 327 (39.1%) | 9 (7.0%) | 10.9% | 36.4% | 0.1655 | no |

Chosen: **all runs agree, no budget/none_without_empty/errors, withhold 4 types, withhold bant/text answers**

