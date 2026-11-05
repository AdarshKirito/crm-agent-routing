# Round 3: ordering the rule chain on development data

Computed by `scripts/dev/chain_order.py` on the used CRMArena-Pro records (rounds 1 and 2, 1,753 tasks, three
runs each), with gate results from `scripts/rewrite_recheck.py` and pins cross-fitted by round. Development
data only: it orders the chain before calibration, it is not a result.

| rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | runs per task |
|---|---|---|---|---|
| runs 1-3 agree on gated types, gate pinned, withhold bant/text answers | 1134 of 1753 (64.7%) | 112 (9.9%) | 11.5% | 3.00 |
| runs 1-3 agree on gated types, gate own, withhold bant/text answers | 1093 of 1753 (62.4%) | 118 (10.8%) | 12.5% | 3.00 |
| all runs agree, withhold bant/text answers | 1180 of 1753 (67.3%) | 130 (11.0%) | 12.6% | 3.00 |
| runs 1-2 agree on gated types, gate pinned, withhold bant/text answers | 1154 of 1753 (65.8%) | 112 (9.7%) | 11.3% | 2.68 |
| runs 1-2 agree on gated types, gate own, withhold bant/text answers | 1132 of 1753 (64.6%) | 125 (11.0%) | 12.7% | 2.68 |
| run 1 on gated types, gate pinned, withhold bant/text answers | 1182 of 1753 (67.4%) | 117 (9.9%) | 11.4% | 2.36 |
| run 1 on gated types, gate own, withhold bant/text answers | 1180 of 1753 (67.3%) | 146 (12.4%) | 14.1% | 2.36 |
