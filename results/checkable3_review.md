# Round 3: a non-blind review of 13 answers

```
vendor/CRMArena/.venv/Scripts/python scripts/dev/checkable3_review.py pull
vendor/CRMArena/.venv/Scripts/python scripts/dev/checkable3_review.py report
```

**The blinded audit the plan pre-registered was not conducted.** Its reader had to judge, from the org's records,
whether the benchmark's key or another answer is right. No reader with that knowledge was available: the owner is
not one, and no second reader was found. A packet was built and sealed (`results/checkable3_audit_seal.md`), and one
item was labelled "unsure"; that label is not used. Twelve of its 25 items had their keys shown while the packet was
being built.

What follows is the author's own review, made with the key in view. It covers the 7 wrong released test answers and
the 6 keys that no reading of the convention check reproduces. For each, it pulls the original org's records
(read-only) and recomputes the answer under the readings of the question's period and of its policy. It says which
reading gives the key and which gives crmroute's answer. It is not blind and not independent, and it is reported
apart from the certificate.

## The 7 wrong released answers

| Task | Type | Key | crmroute (3 runs) | What the records show | Verdict |
|---|---|---|---|---|---|
| 244 | monthly_trend_analysis | August | None | One case in the 11 months, in August. The benchmark's domain details, which aided mode shows the agent, define "significantly higher" as more than every other month. | crmroute wrong |
| 294 | top_issue_identification | a1MWs0000012tvt | None | One case in the window under every reading; its issue is the key. | crmroute wrong |
| 337 | top_issue_identification | a1MWs0000012u0j | None | The key is the top issue of December 2020 to February 2021. The question is dated 2020-02-01, so that winter begins ten months later. In the winter under way on that date (December 2019 to February 2020) the product has no cases, which is crmroute's answer. | ambiguous |
| 356 | top_issue_identification | a1MWs0000012u0j | a1MWs0000012u7B | Under rolling quarters, the org's pinned reading, the key leads 3 to 2. Under calendar quarters the two issues tie 3 to 3. | crmroute wrong under the org's reading |
| 566 | named_entity_disambiguation | Urban Lifestyle Sneakers | Retro Style Sneakers | The contact bought three pairs of sneakers on 2024-12-03; "modern lifestyle sneakers" names the key. | crmroute wrong |
| 1078 | best_region_identification | ID | VA | The key comes from December 2020 to February 2021, which starts after the question's date (2020-10-12), or from quarter-aligned months, which the domain details rule out. December 2019 to February 2020 gives crmroute's VA. | ambiguous |
| 1081 | best_region_identification | GA | TN | "Case closures in November 2020": cases created in November give the key, cases closed in November give crmroute's TN. | ambiguous |

## The 6 keys no reading reproduces

| Task | Type | What reproduces the key | Verdict |
|---|---|---|---|
| 495 | case_routing | The issue most like the case ("Loyalty Program Inquiry"); its agent with the most closed cases is the key. crmroute's runs routed by other issues. | key right; a gap in the check, which read crmroute's queries |
| 759 | handle_time | The minimum-case filter counts every agent who held a case, or its current owner. The task's policy says the filter "applies to the first agent that the case was first assigned to"; under that, the answer is another agent. | key departs from its own policy |
| 774 | handle_time | The same: every agent who held a case, or its current owner. | key departs from its own policy |
| 808 | transfer_count | The same: every agent who held a case. Under the first-agent rule, no agent has more than two cases in the window. | key departs from its own policy |
| 842 | transfer_count | Only agents who made at least one transfer are ranked. Ranking every agent the filter keeps gives a tie of agents with no transfers. crmroute's three runs gave None and two of the tied agents. | key follows a convention the question does not state |
| 887 | transfer_count | The same: only agents with at least one transfer. Ranking every agent gives a tie of agents with none. | key follows a convention the question does not state |

## What it changes

- **Released answers.** Of the 7 released answers wrong by the key, 4 are wrong under every reading the records
  allow. In the other 3 the question has two defensible readings, and crmroute's answer follows one of them.
  - Counting those 3 as right gives 4 wrong of 144 (2.8%; exact one-sided 95% bound 6.2%).
  - Against the shipped key the figure stays 7 of 144 (4.9%; bound 8.9%). The certificate is stated against the
    key, and this review does not replace it.
- **Keys.** Five keys depart from their task's stated policy or follow an unstated convention, and one is right.
  All five are of withheld types: the chosen rule released none of them.
- **Patterns across the benchmark.** The same recomputation was run over every transfer-count and handle-time task
  of the original org (91 of each with a key, all 1,170 single-turn tasks searched; computed after the test). The
  three patterns are reported upstream as CRMArena
  [#31](https://github.com/SalesforceAIResearch/CRMArena/issues/31):
  - **The minimum-case filter counts every agent who held a case.** The policy text says it counts the first
    agent. In 13 tasks the two readings give different answers, and the key follows "every agent" in all 13:
    3 transfer counts (808, 897, 908) and 10 handle times (650, 655, 710, 715, 721, 724, 732, 759, 774, 776).
    The key follows the first-agent rule in none.
  - **"Fewest transfers" ranks only agents with at least one transfer.** That reading reproduces 80 of the 91
    transfer-count keys with the first-agent filter and 83 with the every-agent filter. Ranking every agent
    reproduces 58 and 57. Neither the question nor the policy says agents with no transfers are left out.
  - **"Winter of Y" can name a winter after the question's date.** 10 of the org's 27 "winter of Y" questions are
    dated before December of Y. In both such test tasks reviewed here (337, 1078), the key reads December Y to
    February Y+1 even so.
  - Transfer-count keys for 8 tasks and handle-time keys for 10 are reproduced by no reading tried here.
