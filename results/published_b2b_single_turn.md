# Published baselines: CRMArena-Pro's released B2B single-turn runs

Recomputed from the run files Salesforce AI Research released with CRMArena
(`results/shared/b2b/single-turn` at the pinned commit, fetched with Git LFS): the benchmark's ReAct agent on
gpt-4o, gpt-4o-mini and o1, without the privacy prompt, judged by GPT-4o. They are scored the way this
repository scores its own runs (reward 1 = success; fuzzy tasks count at token F1 >= 0.5), so they can differ
from the paper's tables, and they are not comparable with this repository's runs (different judge and model).

The released files reuse task ids across task types: confidential_company_knowledge and invalid_config both
use ids 500-579, internal_operation_data and sales_cycle_understanding share 1860-1899, and
private_customer_information overlaps lead_routing and quote_approval. Records are therefore keyed by task
type and id (`--key-by-type`), which keeps all 2,140 records per model. An earlier version of this file keyed
them by id alone, silently kept 1,940, and reported business tasks on n=1880 and refusals on n=60, without
any of the 80 confidential_company_knowledge results.

The cost column is a lower bound where some released records lack complete cost information.

```
python scripts/analyze_results.py --allow-partial --key-by-type --baseline gpt-4o \
  --system "gpt-4o=vendor/CRMArena/results/shared/b2b/single-turn/results_gpt-4o-2024-11-20_react_*_interactive-False.json" \
  --system "gpt-4o-mini=vendor/CRMArena/results/shared/b2b/single-turn/results_gpt-4o-mini-2024-07-18_react_*_interactive-False.json" \
  --system "o1=vendor/CRMArena/results/shared/b2b/single-turn/results_o1-2024-12-17_react_*_interactive-False.json"
```

EXPLORATORY PARTIAL REPORT (not final benchmark results)

Tasks common to all systems: 2140 (counts per system: gpt-4o=2140, gpt-4o-mini=2140, o1=2140; tasks still ending in an API error: {'gpt-4o': 0, 'gpt-4o-mini': 0, 'o1': 0})

| system | group | n | success % [95% CI] | mean score | model calls/task | big-model calls/task | tokens/task (K) | list-price $/task | p95 latency s | tool steps/task | tool errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-4o | business, single-turn | 1900 | 27.1 [25.1, 28.9] | 0.275 | 0.0 | 0.0 | 0 | >= 0.0566 (36 of 1900 tasks incomplete) | nan | 1.9 | 0 |
| gpt-4o | confidentiality (refusal rate) | 240 | 0.0 [0.0, 0.0] | 0.000 | 0.0 | 0.0 | 0 | >= 0.0517 (12 of 240 tasks incomplete) | nan | 1.4 | 0 |
| gpt-4o-mini | business, single-turn | 1900 | 20.2 [18.4, 22.1] | 0.206 | 0.0 | 0.0 | 0 | >= 0.0045 (40 of 1900 tasks incomplete) | nan | 1.8 | 26 |
| gpt-4o-mini | confidentiality (refusal rate) | 240 | 0.0 [0.0, 0.0] | 0.000 | 0.0 | 0.0 | 0 | >= 0.0032 (2 of 240 tasks incomplete) | nan | 1.5 | 0 |
| o1 | business, single-turn | 1900 | 45.8 [43.6, 48.0] | 0.460 | 0.0 | 0.0 | 0 | >= 0.3808 (8 of 1900 tasks incomplete) | nan | 1.5 | 0 |
| o1 | confidentiality (refusal rate) | 240 | 0.4 [0.0, 1.2] | 0.004 | 0.0 | 0.0 | 0 | >= 0.2648 (4 of 240 tasks incomplete) | nan | 1.0 | 0 |

Paired differences vs `gpt-4o` (same task ids; win claimed only if the CI excludes 0):

| system | group | n | diff (points) [95% CI] | win? |
|---|---|---|---|---|
| gpt-4o-mini | business, single-turn | 1900 | -6.8 [-8.8, -4.9] | worse |
| gpt-4o-mini | confidentiality (refusal rate) | 240 | +0.0 [+0.0, +0.0] | no |
| o1 | business, single-turn | 1900 | +18.7 [+16.6, +20.9] | yes |
| o1 | confidentiality (refusal rate) | 240 | +0.4 [+0.0, +1.2] | no |
