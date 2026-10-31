# Hints ablation on the held-out test set

System 3 (crmroute, every task on Gemini 3.8 Flash) with the per-task-type hints left out of the solver prompt (`CRMROUTE_TASK_HINTS=0`): the 25 `TaskSpec.hints` lines over the 19 business task types in `agent/app/task_specs.py`. The router's task goal, the answer form, the details to ask for, the general rules and the checker stay, so this measures the per-type hints only, not all of the dev tuning.

It ran on the 194 test tasks after the test run, with the test run's pins (models, thinking level, eval mode, judge and simulated user, task ids, turn limits; `runs/ablation_hints/manifest_*.json`), in `crmroute:nohints`: the test image (`0374d9c6e7b7`, commit `7beda40`) with only `agent/app/config.py` and `agent/app/prompts.py` replaced (`deploy/hints_ablation.Dockerfile`). The harness patch has two changes since the test run, neither of which affects CRMArena-Pro scoring: it copies the agent's last answer check into the run record, and it wraps single-string answers, which only the original CRMArena org has. Nothing was tuned or changed because of this run.

```
python scripts/hints_ablation.py --out results/ablation_hints.md
python scripts/analyze_results.py --system full=runs/test/full --system full_nohints=runs/ablation_hints/full_nohints --baseline full --task-ids data/test.json --big-model 3.8-flash
```

## Summary (`analyze_results.py`)

Complete against the supplied fixed task split.

Tasks common to all systems: 194 (counts per system: full=194, full_nohints=194; tasks still ending in an API error: {'full': 0, 'full_nohints': 0})

| system | group | n | success % [95% CI] | mean score | model calls/task | big-model calls/task | tokens/task (K) | list-price $/task | p95 latency s | tool steps/task | tool errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full | business, single-turn | 114 | 69.3 [61.4, 77.2] | 0.694 | 9.1 | 8.0 | 103 | 0.0427 | 75.8 | 8.1 | 92 |
| full | business, multi-turn | 38 | 50.0 [34.2, 65.8] | 0.500 | 13.6 | 11.3 | 152 | 0.0956 | 152.4 | 11.4 | 47 |
| full | confidentiality (refusal rate) | 42 | 92.9 [83.3, 100.0] | 0.929 | 2.2 | 0.3 | 4 | 0.0021 | 5.1 | 0.3 | 1 |
| full_nohints | business, single-turn | 114 | 64.0 [55.3, 72.8] | 0.644 | 9.8 | 8.7 | 112 | 0.0433 | 113.3 | 8.8 | 101 |
| full_nohints | business, multi-turn | 38 | 39.5 [23.7, 55.3] | 0.395 | 13.2 | 11.0 | 134 | 0.0780 | 117.6 | 11.0 | 36 |
| full_nohints | confidentiality (refusal rate) | 42 | 92.9 [83.3, 100.0] | 0.929 | 2.1 | 0.2 | 3 | 0.0016 | 7.4 | 0.2 | 0 |

Paired differences vs `full` (same task ids; win claimed only if the CI excludes 0):

| system | group | n | diff (points) [95% CI] | win? |
|---|---|---|---|---|
| full_nohints | business, single-turn | 114 | -5.3 [-13.2, +2.6] | no |
| full_nohints | business, multi-turn | 38 | -10.5 [-26.3, +5.3] | no |
| full_nohints | confidentiality (refusal rate) | 42 | +0.0 [+0.0, +0.0] | no |

The p95 latency column is not comparable between the two runs, which ran four weeks apart under different host load.

## Against the ReAct baselines

Paired on the same task ids, 95% bootstrap intervals (5,000 resamples, seed 0, as in `results/robustness_checks.md`). "Best case" counts every baseline task that hit the 250K-token request cap as a baseline success; no crmroute task hit it.

| comparison | group | n | baseline, measured | baseline, best case | crmroute | difference, measured [95% CI] | difference, best case [95% CI] |
|---|---|---|---|---|---|---|---|
| full vs react | business, single-turn | 114 | 56.1% | 63.2% | 69.3% | +13.2 [+5.3, +21.9] | +6.1 [-3.5, +15.8] |
| full vs react | business, multi-turn | 38 | 28.9% | 36.8% | 50.0% | +21.1 [+2.6, +39.5] | +13.2 [-7.9, +34.2] |
| full_nohints vs react | business, single-turn | 114 | 56.1% | 63.2% | 64.0% | +7.9 [+0.9, +14.9] | +0.9 [-7.0, +8.8] |
| full_nohints vs react | business, multi-turn | 38 | 28.9% | 36.8% | 39.5% | +10.5 [-5.3, +26.3] | +2.6 [-15.8, +21.1] |
| full vs react_privacy | business, single-turn | 114 | 50.0% | 55.3% | 69.3% | +19.3 [+11.4, +28.1] | +14.0 [+5.3, +23.7] |
| full vs react_privacy | business, multi-turn | 38 | 21.1% | 23.7% | 50.0% | +28.9 [+10.5, +47.4] | +26.3 [+7.9, +44.7] |
| full_nohints vs react_privacy | business, single-turn | 114 | 50.0% | 55.3% | 64.0% | +14.0 [+7.0, +21.1] | +8.8 [+0.9, +16.7] |
| full_nohints vs react_privacy | business, multi-turn | 38 | 21.1% | 23.7% | 39.5% | +18.4 [+5.3, +34.2] | +15.8 [+0.0, +31.6] |

crmroute tasks ended by the cap (both runs): 0.

## By task type (business, single-turn)

Tasks solved with and without the hints. About 6 tasks per type, so a single type's change is descriptive, not a finding.

| task type | n | with hints | without hints | change |
|---|---|---|---|---|
| quote_approval | 6 | 4 | 0 | -4 |
| sales_cycle_understanding | 6 | 6 | 3 | -3 |
| invalid_config | 6 | 6 | 4 | -2 |
| sales_amount_understanding | 6 | 4 | 2 | -2 |
| monthly_trend_analysis | 6 | 5 | 4 | -1 |
| policy_violation_identification | 6 | 4 | 3 | -1 |
| wrong_stage_rectification | 6 | 4 | 3 | -1 |
| activity_priority | 6 | 5 | 5 | +0 |
| case_routing | 6 | 6 | 6 | +0 |
| knowledge_qa | 6 | 0 | 0 | +0 |
| lead_routing | 6 | 6 | 6 | +0 |
| named_entity_disambiguation | 6 | 5 | 5 | +0 |
| sales_insight_mining | 6 | 0 | 0 | +0 |
| top_issue_identification | 6 | 6 | 6 | +0 |
| best_region_identification | 6 | 5 | 6 | +1 |
| handle_time | 6 | 5 | 6 | +1 |
| transfer_count | 6 | 4 | 5 | +1 |
| conversion_rate_comprehension | 6 | 4 | 6 | +2 |
| lead_qualification | 6 | 0 | 3 | +3 |

Single-turn tasks solved only with the hints: 14; only without them: 8. Multi-turn: 7 and 3.

## Spend

List price, the larger of the task records and the per-call logs (as in `results/robustness_checks.md`; the local judge and simulated user are $0):

| run directory | task records | per-call logs |
|---|---|---|
| `runs/ablation_hints` | $7.97 | $7.97 |
