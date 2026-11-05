# Round 3, development run D1 on the original org's used tasks

One routed run of round 2's unchanged image (658df1a6bc7f) on the 510 used single-turn tasks
(`data/checkable3_dev.json`), computed by `scripts/dev/d1_summary.py`. Development data, not a result.

| predicted type | tasks | right | released by run 1 clean | wrong among them |
|---|---|---|---|---|
| best_region_identification | 57 | 42 | 56 | 14 (25.0%) |
| case_routing | 56 | 56 | 56 | 0 (0.0%) |
| handle_time | 57 | 36 | 57 | 21 (36.8%) |
| knowledge_qa | 55 | 46 | 0 | 0 (0.0%) |
| monthly_trend_analysis | 57 | 42 | 57 | 15 (26.3%) |
| named_entity_disambiguation | 56 | 55 | 56 | 1 (1.8%) |
| policy_violation_identification | 57 | 21 | 57 | 36 (63.2%) |
| top_issue_identification | 60 | 59 | 60 | 1 (1.7%) |
| transfer_count | 55 | 39 | 55 | 16 (29.1%) |

Right overall: 396 of 510 (77.6%).

Competence map, types wrong more than 15%: best_region_identification, handle_time, monthly_trend_analysis, policy_violation_identification, transfer_count.
Competence map, types wrong more than 20%: best_region_identification, handle_time, monthly_trend_analysis, policy_violation_identification, transfer_count.

List price: $14.08 in all, $0.0276 per task against the plan's $0.0311 (-11.2%; the stop rule acts above +25%).

## Receipt flags (run 1)

| flag (first run) | answers | right |
|---|---|---|
| (none) | 193 | 150 (78%) |
| errors | 174 | 147 (84%) |
| budget | 129 | 75 (58%) |
| period_unfiltered | 66 | 64 (97%) |
| none_without_empty | 49 | 32 (65%) |
| blocked | 44 | 43 (98%) |
| truncated_support | 10 | 3 (30%) |
| no_data | 1 | 0 (0%) |

