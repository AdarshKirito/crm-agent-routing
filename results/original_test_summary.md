# Original CRMArena org: held-out test (2026-10-04)

Does crmroute carry over to an org it was not built on? `data/original_test.json`: 90 single-turn tasks of the
original CRMArena org (10 per type, 9 types), disjoint from its dev list, run once after the org's routing
table was fitted on dev and committed (`b4c87f6`). The agent's code and per-task hints are the CRMArena-Pro
ones; the org added only its schema text, router examples from its non-test tasks and a knowledge index
(`results/original_dev_summary.md`). Same pins as the CRMArena-Pro test run: Vertex AI Gemini 3.8 Flash and 3.1
Flash-Lite, thinking `low`, eval mode `aided`, judge local `ollama_chat/qwen3:8b` for every system.

| system | what runs | image / table | list-price spend (90 tasks) |
|---|---|---|---|
| react | the benchmark's ReAct agent on 3.8 Flash | (no agent image) | $6.11 |
| full | crmroute, every task on 3.8 Flash | `crmroute:org` `c0d1e2920b8e` | $3.67 |
| routed | crmroute with the org's own routing table | same image, `routing_original.yaml` | $2.80 |

```
python scripts/analyze_results.py --system react=runs/original_test/react --system full=runs/original_test/full   --system routed=runs/original_test/routed --baseline react --task-ids data/original_test.json   --big-model 3.8-flash --out results/original_test_summary.md
```

Complete against the supplied fixed task split.

Tasks common to all systems: 90 (counts per system: react=90, full=90, routed=90; tasks still ending in an API error: {'react': 0, 'full': 0, 'routed': 0})

| system | group | n | success % [95% CI] | mean score | model calls/task | big-model calls/task | tokens/task (K) | list-price $/task | p95 latency s | tool steps/task | tool errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| react | business, single-turn | 90 | 75.6 [66.7, 84.4] | 0.738 | 7.0 | 7.0 | 174 | 0.0679 | nan | 5.4 | 0 |
| full | business, single-turn | 90 | 81.1 [73.3, 88.9] | 0.804 | 8.9 | 7.7 | 96 | 0.0408 | 42.4 | 7.8 | 80 |
| routed | business, single-turn | 90 | 82.2 [74.4, 90.0] | 0.817 | 8.3 | 5.2 | 84 | 0.0311 | 45.4 | 7.2 | 70 |

Paired differences vs `react` (same task ids; win claimed only if the CI excludes 0):

| system | group | n | diff (points) [95% CI] | win? |
|---|---|---|---|---|
| full | business, single-turn | 90 | +5.6 [-3.3, +14.4] | no |
| routed | business, single-turn | 90 | +6.7 [-1.1, +14.4] | no |

`analyze_results.py ... --baseline full` (the cost of routing on this org):

| system | group | n | diff (points) [95% CI] | win? |
|---|---|---|---|---|
| routed | business, single-turn | 90 | +1.1 [-5.6, +7.8] | no |

## What this shows

- **Ahead, but not significantly, on an unseen org.** crmroute scores 81.1% (3.8 Flash only) and 82.2% (routed)
  against 75.6% for ReAct on the same model: +5.6 and +6.7 points, with 95% intervals that include zero at n=90.
  The gap is smaller than on CRMArena-Pro (+13 to +15) mainly because ReAct does much better here (75.6% vs
  56.1%), on a 16-object schema without opportunities, leads or quotes.
- **Cheaper.** 40% lower cost per task than ReAct with every task on 3.8 Flash ($0.041 vs $0.068) and 54% lower
  routed ($0.031); bounded tool results keep a task at 96K tokens against ReAct's 174K.
- **The org's own routing table works.** Fitted on 90 of the org's dev tasks with the shipped rule, it sent
  30 of the 90 test tasks (3 task types) to Flash-Lite and cut cost 24% against 3.8 Flash only, with no
  measurable loss (+1.1 points, interval spanning zero).
- **The router needed no new examples.** It named the right task type for all 90 test requests; built from the
  CRMArena-Pro examples alone it also scores 90/90 offline (`results/router_transfer.json`). The original
  org's questions come from the same benchmark family, so this is transfer within it, not to a company's
  own phrasing.

## Run notes

- Scoring needed a harness fix first (`a918dc2`): the original CRMArena tasks store one answer (a string or
  None) where CRMArena-Pro stores a list, and the shared evaluator marked every original-org answer wrong.
- The cost column is a lower bound only because some Prompt Guard calls (Groq free tier, about $0.000003 each)
  were rate-limited and have no usage record; ReAct's latency is not recorded by the harness.
