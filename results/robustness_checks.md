# Robustness checks on the headline numbers

```
python scripts/robustness_checks.py --out results/robustness_checks.md
```

## 1. The 250K-token request cap (test run)

`runs/test`, `data/test.json`. Tasks scored as failures because one request went over the cap:

| system | business, single-turn | business, multi-turn | confidentiality | total |
|---|---|---|---|---|
| react | 8 | 3 | 6 | 17 |
| react_privacy | 6 | 1 | 0 | 7 |
| full | 0 | 0 | 0 | 0 |
| routed | 0 | 0 | 0 | 0 |

Business success with every capped baseline task counted as a success instead (the best case for the baseline), paired on the same task ids:

| comparison | group | n | baseline, measured | baseline, best case | crmroute | difference, best case [95% CI] |
|---|---|---|---|---|---|---|
| full vs react | business, single-turn | 114 | 56.1% | 63.2% | 69.3% | +6.1 [-3.5, +15.8] |
| full vs react | business, multi-turn | 38 | 28.9% | 36.8% | 50.0% | +13.2 [-7.9, +34.2] |
| routed vs react | business, single-turn | 114 | 56.1% | 63.2% | 71.1% | +7.9 [-0.9, +17.5] |
| routed vs react | business, multi-turn | 38 | 28.9% | 36.8% | 47.4% | +10.5 [-7.9, +28.9] |
| full vs react_privacy | business, single-turn | 114 | 50.0% | 55.3% | 69.3% | +14.0 [+5.3, +23.7] |
| full vs react_privacy | business, multi-turn | 38 | 21.1% | 23.7% | 50.0% | +26.3 [+7.9, +44.7] |
| routed vs react_privacy | business, single-turn | 114 | 50.0% | 55.3% | 71.1% | +15.8 [+7.0, +25.4] |
| routed vs react_privacy | business, multi-turn | 38 | 21.1% | 23.7% | 47.4% | +23.7 [+5.3, +42.1] |

## 2. Customer-facing business requests refused by the guard

The benchmark runs knowledge_qa and named_entity_disambiguation tasks as customer sessions, so the policy check screens them alongside the confidential requests; refusing one is a false refusal.

| run | single-turn refused | multi-turn refused | refused tasks |
|---|---|---|---|
| test, crmroute 3.8 Flash only | 0 of 12 | 0 of 4 | none |
| test, crmroute routed | 0 of 12 | 1 of 4 | b2b/1987 (multi-turn, named_entity_disambiguation) |
| fresh, measured agent | 0 of 72 | 1 of 4 | b2b/1963 (multi-turn, named_entity_disambiguation) |
| fresh, fixed agent | 0 of 72 | 0 of 4 | none |

## 3. Fresh tasks that are labelled router examples

`agent/app/data/router_examples.jsonl` (1760 examples) holds 0 of the 194 test tasks and these fresh tasks:

| group | fresh tasks | also router examples |
|---|---|---|
| business, single-turn | 174 | 57 |
| business, multi-turn | 38 | 17 |
| confidentiality | 408 | 220 |

Confidential requests refused, `runs/fresh_before/routed` vs `runs/fresh_after/routed`:

| requests | n | before | after | difference [95% CI] |
|---|---|---|---|---|
| all | 408 | 96.3% | 99.0% | +2.7 [+1.2, +4.4] |
| in the example file | 220 | 99.1% | 100.0% | +0.9 [+0.0, +2.3] |
| not in the example file | 188 | 93.1% | 97.9% | +4.8 [+2.1, +8.0] |
| not in the example file, confidential_company_knowledge | 64 | 79.7% | 93.8% | +14.1 [+6.2, +23.4] |
| not in the example file, internal_operation_data | 61 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] |
| not in the example file, private_customer_information | 63 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] |

## 4. List-price spend

Model calls at list price (agent, policy classifier, Prompt Guard, and any judge or simulated-user API calls; local Ollama is $0). Per run directory, the larger of the task records (failed attempts included) and the per-call logs: the logs also hold calls of tasks that never finished, such as a run stopped mid-task, but the earliest runs logged no prices. Runs on free tiers (the 2026-09-29 pilot and the PR-eval baseline runs) are counted at list price although they were not billed. Prompt Guard calls rejected with 429 have no usage record.

| phase | run directories | task records | list-price spend |
|---|---|---|---|
| before the test | ci ($0.16), ci2 ($0.12), ci3 ($0.15), dev ($7.07), dev2 ($3.48), dev3 ($11.83), dev_react_probe ($3.31), dev_react_probe_multi ($1.70), dev_small ($0.42), devmt_check ($0.27), smoke ($0.02), smoke_pipeline ($0.02), smoke_vertex ($0.02), smoke_vertex2 ($0.64), test_small ($0.36), trace ($0.09) | 1317 | $29.66 |
| test run | test ($42.66) | 776 | $42.66 |
| after the test | ablation_hints ($7.97), fresh_after ($7.30), fresh_before ($7.53), original_dev ($5.00), original_dev_oom_attempt ($0.02), original_smoke ($0.38), original_smoke2 ($0.35), original_test ($12.58) | 1913 | $41.14 |
| all | | | $113.46 |
