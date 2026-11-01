# Checkable answers: the certified release rules

```
python scripts/checkable_report.py --stage calibration
```

Learn-then-Test on the calibration runs (`data/checkable_calibration.json`), alpha 0.1, delta 0.1, the pre-registered family in its order; free-text and BANT answers are never released. Each table stops at the first rule that is not certified; the chosen rule is the last certified one before it. These choices are committed before any test result is read.

## crmroute, three runs (two routed, one on 3.8 Flash)

456 calibration tasks, 3 run(s) each.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified |
|---|---|---|---|---|---|---|
| agree>=3, no budget/none_without_empty/errors, withhold bant/text answers | 168 of 456 (36.8%) | 10 (6.0%) | 9.0% | 34.6% | 0.0454 | yes |
| agree>=3, no budget/none_without_empty, withhold bant/text answers | 223 of 456 (48.9%) | 19 (8.5%) | 11.4% | 44.7% | 0.2721 | no |

Certified rule: **agree>=3, no budget/none_without_empty/errors, withhold bant/text answers**

## ReAct with the privacy prompt, one run

456 calibration tasks, 1 run(s) each.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified |
|---|---|---|---|---|---|---|
| agree>=1, no budget/none_without_empty/errors, withhold bant/text answers | 292 of 456 (64.0%) | 88 (30.1%) | 33.8% | 44.7% | 1.0000 | no |

Certified rule: **none (every answer is withheld)**

## crmroute, first routed run alone

456 calibration tasks, 1 run(s) each.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified |
|---|---|---|---|---|---|---|
| agree>=1, no budget/none_without_empty/errors, withhold bant/text answers | 245 of 456 (53.7%) | 37 (15.1%) | 18.5% | 45.6% | 0.9955 | no |

Certified rule: **none (every answer is withheld)**

## crmroute, three runs, calibrated on B2B only and applied to B2C

228 calibration tasks, 3 run(s) each.

| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score | p-value | certified |
|---|---|---|---|---|---|---|
| agree>=3, no budget/none_without_empty/errors, withhold bant/text answers | 83 of 228 (36.4%) | 6 (7.2%) | 12.3% | 33.8% | 0.2644 | no |

Certified rule: **none (every answer is withheld)**

