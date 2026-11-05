# Round 3 go/no-go checks on CRMArena-Pro records

Computed by `scripts/dev/gonogo.py` from `scripts/rewrite_recheck.py` output, with the definitions and
thresholds committed in `docs/checkable3_devlog.md` before any of them was computed. These are in-sample
development figures: the engine was written while reading these records.

## Run answers of the six types, by predicted type

| type | run answers | C1 check completes | C2 own level passes | own passes over one group |
|---|---|---|---|---|
| best_region_identification | 285 | 284 of 285 (99.6%) | 251 of 285 (88.1%) | 29 |
| case_routing | 282 | 272 of 282 (96.5%) | 253 of 282 (89.7%) | 98 |
| handle_time | 267 | 261 of 267 (97.8%) | 222 of 267 (83.1%) | 61 |
| monthly_trend_analysis | 273 | 270 of 273 (98.9%) | 171 of 273 (62.6%) | 74 |
| top_issue_identification | 285 | 282 of 285 (98.9%) | 265 of 285 (93.0%) | 149 |
| transfer_count | 279 | 279 of 279 (100.0%) | 237 of 279 (84.9%) | 84 |
| all | 1671 | 1648 of 1671 (98.6%) | 1399 of 1671 (83.7%) | 495 |

Why a check did not complete: no live re-run derived an answer: 10, no applicable query: 8, unrewritable: 5.

C3 chance control: the own level passes for 163 of 1461 (11.2%) answers on the other task's receipt.

## Readings the other round's keys exclude or pin

| tasks judged | readings learned from | excluded | pinned (reported only) |
|---|---|---|---|
| round 1 | round 2 | none | date_field=CreatedDate, past_months_years=rolling, past_quarters=rolling, rolling_end=today_counted, rolling_end=today_not_counted, season_months=meteorological, ties=first, ties=none |
| round 2 | round 1 | none | date_field=CreatedDate, past_months_years=rolling, past_quarters=rolling, rolling_end=today_not_counted, season_months=meteorological, season_year=december_of_y, ties=first, ties=none |

## The gate: 471 unanimous tasks (18 wrong, 453 right)

| level | wrong: pass / fail / unchecked | right: pass / fail / unchecked |
|---|---|---|
| own | 6 / 12 / 0 | 377 / 76 / 0 |
| allowed | 0 / 18 / 0 | 316 / 137 / 0 |
| declared | 0 / 18 / 0 | 316 / 137 / 0 |

Withheld at the allowed level: 18 of 18 (100.0%) wrong answers (C4), 137 of 453 (30.2%) right answers (C5). Unanimous wrong tasks that pass the own level: b2c/1095 (withheld), b2c/1159 (withheld), b2c/1237 (withheld), b2c/1272 (withheld), b2c/1275 (withheld), b2c/156 (withheld) (C6 counts the withheld ones: 6).

C7 rescue (reported only), 86 tasks whose runs disagree: the key is among the declared readings' answers in 78 of 86 (90.7%), among the runs' answers in 75 of 86 (87.2%).

C8 portability: checks complete for 36 of 51 (70.6%) of ReAct's checkable answers on the original org.

## Against the committed thresholds

| check | value | GO if | result |
|---|---|---|---|
| C1 | 98.6% | at least 90% | pass |
| C2 | 83.7% | at least 85% | FAIL |
| C3 | 11.2% | at most 10% | FAIL |
| C4 | 100.0% | at least 40% | pass |
| C5 | 30.2% | at most 8% | FAIL |
| C6 | 6 | at least 2 | pass |
| C8 | 70.6% | at least 85% | FAIL |

C1 or C2 failed overall, so the development log restricts the gate to the types that pass both: best_region_identification, case_routing, top_issue_identification.

## The gate on those types: 257 unanimous tasks (9 wrong, 248 right)

| level | wrong: pass / fail / unchecked | right: pass / fail / unchecked |
|---|---|---|
| own | 2 / 7 / 0 | 226 / 22 / 0 |
| allowed | 0 / 9 / 0 | 199 / 49 / 0 |
| declared | 0 / 9 / 0 | 199 / 49 / 0 |

Withheld at the allowed level: 9 of 9 (100.0%) wrong answers (C4), 49 of 248 (19.8%) right answers (C5). Unanimous wrong tasks that pass the own level: b2c/1095 (withheld), b2c/1159 (withheld) (C6 counts the withheld ones: 2).

| check | value | GO if | result |
|---|---|---|---|
| C4 (restricted) | 100.0% | at least 40% | pass |
| C5 (restricted) | 19.8% | at most 8% | FAIL |
| C6 (restricted) | 2 | at least 2 | pass |
