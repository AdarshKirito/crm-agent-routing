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
| monthly_trend_analysis | 273 | 273 of 273 (100.0%) | 174 of 273 (63.7%) | 75 |
| top_issue_identification | 285 | 285 of 285 (100.0%) | 270 of 285 (94.7%) | 153 |
| transfer_count | 279 | 279 of 279 (100.0%) | 237 of 279 (84.9%) | 84 |
| all | 1671 | 1654 of 1671 (99.0%) | 1407 of 1671 (84.2%) | 500 |

Why a check did not complete: no live re-run derived an answer: 10, unrewritable: 5, no applicable query: 2.

C3 chance control: the own level passes for 163 of 1461 (11.2%) answers on the other task's receipt.

## Readings the other round's keys exclude or pin

| tasks judged | readings learned from | excluded | pinned (reported only) |
|---|---|---|---|
| round 1 | round 2 | none | date_field=CreatedDate, past_months_years=rolling, past_quarters=rolling, rolling_end=today_counted, rolling_end=today_not_counted, season_months=meteorological, ties=first, ties=none |
| round 2 | round 1 | none | date_field=CreatedDate, past_months_years=rolling, past_quarters=rolling, rolling_end=today_not_counted, season_months=meteorological, season_year=december_of_y, ties=first, ties=none |

## The gate: 471 unanimous tasks (18 wrong, 453 right)

| level | wrong: pass / fail / unchecked | right: pass / fail / unchecked |
|---|---|---|
| own | 6 / 12 / 0 | 378 / 75 / 0 |
| allowed | 0 / 18 / 0 | 317 / 136 / 0 |
| declared | 0 / 18 / 0 | 317 / 136 / 0 |

Withheld at the allowed level: 18 of 18 (100.0%) wrong answers (C4), 136 of 453 (30.0%) right answers (C5). Unanimous wrong tasks that pass the own level: b2c/1095 (withheld), b2c/1159 (withheld), b2c/1237 (withheld), b2c/1272 (withheld), b2c/1275 (withheld), b2c/156 (withheld) (C6 counts the withheld ones: 6).

C7 rescue (reported only), 86 tasks whose runs disagree: the key is among the declared readings' answers in 78 of 86 (90.7%), among the runs' answers in 75 of 86 (87.2%).

C8 portability: checks complete for 47 of 51 (92.2%) of ReAct's checkable answers on the original org.

## Against the committed thresholds

| check | value | GO if | result |
|---|---|---|---|
| C1 | 99.0% | at least 90% | pass |
| C2 | 84.2% | at least 85% | FAIL |
| C3 | 11.2% | at most 10% | FAIL |
| C4 | 100.0% | at least 40% | pass |
| C5 | 30.0% | at most 8% | FAIL |
| C6 | 6 | at least 2 | pass |
| C8 | 92.2% | at least 85% | pass |

C1 or C2 failed overall, so the development log restricts the gate to the types that pass both: best_region_identification, case_routing, top_issue_identification.

## The gate on those types: 257 unanimous tasks (9 wrong, 248 right)

| level | wrong: pass / fail / unchecked | right: pass / fail / unchecked |
|---|---|---|
| own | 2 / 7 / 0 | 227 / 21 / 0 |
| allowed | 0 / 9 / 0 | 200 / 48 / 0 |
| declared | 0 / 9 / 0 | 200 / 48 / 0 |

Withheld at the allowed level: 9 of 9 (100.0%) wrong answers (C4), 48 of 248 (19.4%) right answers (C5). Unanimous wrong tasks that pass the own level: b2c/1095 (withheld), b2c/1159 (withheld) (C6 counts the withheld ones: 2).

| check | value | GO if | result |
|---|---|---|---|
| C4 (restricted) | 100.0% | at least 40% | pass |
| C5 (restricted) | 19.4% | at most 8% | FAIL |
| C6 (restricted) | 2 | at least 2 | pass |
