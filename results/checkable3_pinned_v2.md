# Round 3, exploratory: the gate over pinned readings only

Computed by `scripts/dev/pinned_gate.py` after the go/no-go decision (NO-GO, `results/checkable3_gonogo.md`),
on the same in-sample CRMArena-Pro records. Pins are cross-fitted by round, as in the go/no-go. This is a
post-hoc analysis: it can motivate an arm to pre-register and test on new data, not a result.

| tasks judged | pinned readings (from the other round's keys) |
|---|---|
| round 1 | date_field: CreatedDate; past_months_years: rolling; past_quarters: rolling; rolling_end: today_counted, today_not_counted; season_months: meteorological; ties: first, none |
| round 2 | date_field: CreatedDate; past_months_years: rolling; past_quarters: rolling; rolling_end: today_not_counted; season_months: meteorological; season_year: december_of_y; ties: first, none |

| variant | type | unanimous wrong held back | unanimous right held back |
|---|---|---|---|
| own level required | best_region_identification | 4 of 4 (100.0%) | 7 of 69 (10.1%) |
| own level required | case_routing | 5 of 5 (100.0%) | 2 of 87 (2.3%) |
| own level required | handle_time | 2 of 2 (100.0%) | 9 of 65 (13.8%) |
| own level required | monthly_trend_analysis | 1 of 1 (100.0%) | 39 of 81 (48.1%) |
| own level required | top_issue_identification | 0 of 0 | 13 of 92 (14.1%) |
| own level required | transfer_count | 6 of 6 (100.0%) | 8 of 59 (13.6%) |
| own level required | all | 18 of 18 (100.0%) | 78 of 453 (17.2%) |
| readings decide where they exist | best_region_identification | 4 of 4 (100.0%) | 1 of 69 (1.4%) |
| readings decide where they exist | case_routing | 5 of 5 (100.0%) | 2 of 87 (2.3%) |
| readings decide where they exist | handle_time | 2 of 2 (100.0%) | 7 of 65 (10.8%) |
| readings decide where they exist | monthly_trend_analysis | 1 of 1 (100.0%) | 11 of 81 (13.6%) |
| readings decide where they exist | top_issue_identification | 0 of 0 | 0 of 92 (0.0%) |
| readings decide where they exist | transfer_count | 6 of 6 (100.0%) | 7 of 59 (11.9%) |
| readings decide where they exist | all | 18 of 18 (100.0%) | 28 of 453 (6.2%) |
