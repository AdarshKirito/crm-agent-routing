# Round 3, G2: the pinned-reading gate on the original org's development run

Computed by `scripts/dev/g2.py` from `scripts/rewrite_recheck.py --records d1`, with the check and its bars
committed in `docs/checkable3_devlog.md` before D1 ran. D1 is one routed run of round 2's image on the
original org's 510 used tasks; these are development figures on used tasks, not a test.

| judged half | pinned readings (from the other half's keys) | excluded |
|---|---|---|
| even ids | date_field: ClosedDate, CreatedDate; past_months_years: rolling; past_quarters: rolling; rolling_end: today_counted, today_not_counted; season_months: meteorological; season_year: december_of_y; ties: first, none | none |
| odd ids | date_field: CreatedDate; past_months_years: rolling; past_quarters: rolling; rolling_end: today_counted, today_not_counted; season_months: meteorological | none |

| level | type | run answers | check completes | wrong held back | right held back |
|---|---|---|---|---|---|
| pinned, readings decide (G2) | best_region_identification | 57 | 56 of 57 (98.2%) | 14 of 15 (93.3%) | 0 of 42 (0.0%) |
| pinned, readings decide (G2) | case_routing | 56 | 54 of 56 (96.4%) | 0 of 0 | 2 of 56 (3.6%) |
| pinned, readings decide (G2) | handle_time | 57 | 51 of 57 (89.5%) | 15 of 21 (71.4%) | 4 of 36 (11.1%) |
| pinned, readings decide (G2) | monthly_trend_analysis | 57 | 48 of 57 (84.2%) | 7 of 15 (46.7%) | 21 of 42 (50.0%) |
| pinned, readings decide (G2) | top_issue_identification | 60 | 52 of 60 (86.7%) | 1 of 1 (100.0%) | 13 of 59 (22.0%) |
| pinned, readings decide (G2) | transfer_count | 55 | 55 of 55 (100.0%) | 13 of 16 (81.2%) | 2 of 39 (5.1%) |
| pinned, readings decide (G2) | all | 342 | 316 of 342 (92.4%) | 50 of 68 (73.5%) | 42 of 274 (15.3%) |
| pinned, own level required | best_region_identification | 57 | 56 of 57 (98.2%) | 14 of 15 (93.3%) | 0 of 42 (0.0%) |
| pinned, own level required | case_routing | 56 | 54 of 56 (96.4%) | 0 of 0 | 2 of 56 (3.6%) |
| pinned, own level required | handle_time | 57 | 51 of 57 (89.5%) | 15 of 21 (71.4%) | 6 of 36 (16.7%) |
| pinned, own level required | monthly_trend_analysis | 57 | 48 of 57 (84.2%) | 7 of 15 (46.7%) | 22 of 42 (52.4%) |
| pinned, own level required | top_issue_identification | 60 | 52 of 60 (86.7%) | 1 of 1 (100.0%) | 16 of 59 (27.1%) |
| pinned, own level required | transfer_count | 55 | 55 of 55 (100.0%) | 13 of 16 (81.2%) | 2 of 39 (5.1%) |
| pinned, own level required | all | 342 | 316 of 342 (92.4%) | 50 of 68 (73.5%) | 48 of 274 (17.5%) |
| allowed (the go/no-go level) | best_region_identification | 57 | 56 of 57 (98.2%) | 15 of 15 (100.0%) | 12 of 42 (28.6%) |
| allowed (the go/no-go level) | case_routing | 56 | 54 of 56 (96.4%) | 0 of 0 | 2 of 56 (3.6%) |
| allowed (the go/no-go level) | handle_time | 57 | 51 of 57 (89.5%) | 16 of 21 (76.2%) | 8 of 36 (22.2%) |
| allowed (the go/no-go level) | monthly_trend_analysis | 57 | 48 of 57 (84.2%) | 7 of 15 (46.7%) | 22 of 42 (52.4%) |
| allowed (the go/no-go level) | top_issue_identification | 60 | 52 of 60 (86.7%) | 1 of 1 (100.0%) | 21 of 59 (35.6%) |
| allowed (the go/no-go level) | transfer_count | 55 | 55 of 55 (100.0%) | 13 of 16 (81.2%) | 3 of 39 (7.7%) |
| allowed (the go/no-go level) | all | 342 | 316 of 342 (92.4%) | 52 of 68 (76.5%) | 68 of 274 (24.8%) |
| declared | best_region_identification | 57 | 56 of 57 (98.2%) | 15 of 15 (100.0%) | 12 of 42 (28.6%) |
| declared | case_routing | 56 | 54 of 56 (96.4%) | 0 of 0 | 2 of 56 (3.6%) |
| declared | handle_time | 57 | 51 of 57 (89.5%) | 16 of 21 (76.2%) | 8 of 36 (22.2%) |
| declared | monthly_trend_analysis | 57 | 48 of 57 (84.2%) | 7 of 15 (46.7%) | 22 of 42 (52.4%) |
| declared | top_issue_identification | 60 | 52 of 60 (86.7%) | 1 of 1 (100.0%) | 21 of 59 (35.6%) |
| declared | transfer_count | 55 | 55 of 55 (100.0%) | 13 of 16 (81.2%) | 3 of 39 (7.7%) |
| declared | all | 342 | 316 of 342 (92.4%) | 52 of 68 (76.5%) | 68 of 274 (24.8%) |

| check | value | GO if | result |
|---|---|---|---|
| G2a | 92.4% | at least 85% | pass |
| G2b | 73.5% | at least 40% | pass |
| G2c | 15.3% | at most 8% | FAIL |
