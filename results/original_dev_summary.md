# Original CRMArena org: dev runs and its own routing table (2026-10-04)

The original CRMArena org is an org crmroute was not built on: its own Salesforce data and schema
(16 objects, no opportunities, leads or quotes), 9 task types, single-turn only. The agent's code and
per-task hints are unchanged from the CRMArena-Pro work; only the org's schema text, router examples
(from its non-test tasks, `scripts/add_org.py`) and knowledge index were added.

Dev: `data/original_dev.json`, 10 tasks per type (90), disjoint from `data/original_test.json`. Both
crmroute solvers ran every dev task: `full` (Gemini 3.8 Flash only) and `small` (Gemini 3.1 Flash-Lite only).
Image `crmroute:org` `c0d1e2920b8e` (built from `21e112f`), router examples
`router_examples.jsonl,router_examples_original.jsonl`, the test run's other pins. A first attempt stopped
when two containers embedded the router examples at once and one ran out of memory; it is kept in
`runs/original_dev_oom_attempt` and was replaced by this run after the image gained the embedding cache.

```
python scripts/analyze_results.py --system full=runs/original_dev/full --system small=runs/original_dev/agent_small   --task-ids data/original_dev.json --big-model 3.8-flash --out results/original_dev_summary.md
python scripts/fit_routing.py --org original --big runs/original_dev/full --small runs/original_dev/agent_small   --dev-split data/original_dev.json --test-split data/original_test.json --out agent/app/data/routing_original.yaml
```

Complete against the supplied fixed task split.

Tasks common to all systems: 90 (counts per system: full=90, small=90; tasks still ending in an API error: {'full': 0, 'small': 0})

| system | group | n | success % [95% CI] | mean score | model calls/task | big-model calls/task | tokens/task (K) | list-price $/task | p95 latency s | tool steps/task | tool errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full | business, single-turn | 90 | 78.9 [70.0, 86.7] | 0.788 | 9.1 | 7.9 | 103 | >= 0.0426 (9 of 90 tasks incomplete) | 48.7 | 8.0 | 78 |
| small | business, single-turn | 90 | 70.0 [60.0, 78.9] | 0.703 | 7.0 | 0.0 | 60 | >= 0.0130 (6 of 90 tasks incomplete) | 38.2 | 6.0 | 68 |

The routing fit (`agent/app/data/routing_original.yaml`, margin 2 points, at least 8 tasks per type) sends
3 of the 9 task types to Flash-Lite: best_region_identification (big 70%, small 80%), case_routing (100%,
100%) and monthly_trend_analysis (80%, 80%). The other six stay on 3.8 Flash. The cost column is a lower
bound only because some Prompt Guard calls (Groq free tier, about $0.000003 each) were rate-limited and
have no usage record.
