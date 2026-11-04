# Checkable answers, round 3 (pre-registration)

Round 3 runs round 2's agent, unchanged, on an org it was not built on: the original CRMArena org's 660
single-turn tasks that no earlier split, development run or router example used. It asks two questions.

1. **Replication, the primary question.** Learn-then-Test, run as in rounds 1 and 2, certifies a release
   rule on one half of these tasks. Does its risk hold on the other half?
2. **A secondary hypothesis.** A gate recomputes an answer from the run's own queries, rewritten for this
   org's conventions as learned from used tasks and re-run live. On three task types, does it hold back
   wrong answers more often than right ones?

Development is logged in `docs/checkable3_devlog.md`. This page fixes everything before any fresh task runs,
and nothing on it changes after the first fresh run starts.

## What was seen before this page

- **Fresh tasks.** Planning looked at the fresh tasks' question wording and answer forms: for example, how
  many name a season and how many keys say None. No fresh task's run or key value was read, and none set
  anything here.
- **The convention gate on the used CRMArena-Pro records was NO-GO** (`results/checkable3_gonogo.md`). It
  asked every reading the keys do not exclude. It held back all 18 unanimous wrong answers, but also 30.2% of
  the right ones, against a bar of at most 8%.
- **The pinned-reading gate was chosen after seeing those records.** It asks only the readings the used keys
  pin. In-sample, it held back 18 of 18 unanimous wrong answers and 6.2% of the right ones
  (`results/checkable3_pinned_v2.md`).
- **G2 tested the pinned gate on the original org's 510 used tasks and failed on cost**
  (`results/checkable3_g2.md`). Its bars were committed before the development run D1 existed. It held back
  50 of 68 wrong answers (73.5%) and 42 of 274 right ones (15.3%). Most of the cost came from monthly trend
  (21 of 42) and top issue (13 of 59). On best region, case routing and transfer count it held back at most
  5.1% of right answers.
- **D1 itself** (`results/checkable3_d1.md`): 396 of 510 right (77.6%), at $0.0276 per task at list price.
- **The freeze.** After reading D1, and before any fresh task, the freeze was changed in two ways. The
  single-run competence maps are followed by maps scaled to three-run risk and then by no map. The gate's
  secondary analysis is limited to its three low-cost types. Both changes and their reasons are in the dev
  log.

## Agent, runs and tasks

- **Agent.** Image `crmroute:checkable` (658df1a6bc7f) with round 2's settings: Gemini 3.8 Flash and 3.1
  Flash-Lite on Vertex AI at thinking level low, temperature 1.0 and no seed, and the local qwen3:8b judge.
  It uses the original org's routing table (`agent/app/data/routing_original.yaml`) and both router-example
  files.
- **crmroute, three runs per task:** routed run 1, routed run 2, and a run with every task on 3.8 Flash
  (`full`).
- **Baseline:** the benchmark's ReAct agent on 3.8 Flash, one run per task. This org has no confidentiality
  tasks, so it runs with its plain prompt.
- **The split.** `vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --round3 --seed 20261103`
  halves the 660 tasks at random within each task type. That gives `data/checkable3_calibration.json` (327)
  and `data/checkable3_test.json` (333). Both are committed before any run.
- **Gate results.** After the runs, `scripts/rewrite_recheck.py --records checkable3_<half>` (and
  `_react`) re-checks every run's receipt live. The pinned readings are frozen in
  `data/conventions_original.yaml`.

## The chain

`results/checkable3_frozen.json` holds the chain: 15 rules, built unchanged by
`scripts/checkable3_report.py`.

- Every rule needs all of a task's runs to give the same answer and be clean. Free-text and BANT answers are
  never released.
- The rules differ only in the task types they withhold and in their soft flags.
- The order is round 2's chain with D1's single-run maps at 15% and 20%. Then come maps at 27.9% and 37.2%,
  the same thresholds scaled to three-run risk, and then no map. Each map comes at round 2's three flag
  levels, strictest first.

Fixed-sequence Learn-then-Test at alpha = delta = 0.10, with exact binomial p-values, tests the rules in this
order and stops at the first that is not certified. The chosen rule is the certified rule that answers the
most calibration tasks. ReAct gets the same chain. The chosen rules are committed to
`results/checkable3_rules.json` before the test half launches.

## Outcomes

Primary outcomes are measured on crmroute's three runs, on the test half:

| # | Outcome | Bar |
|---|---|---|
| P1 | A rule of the chain certifies on the calibration half | alpha = delta = 0.10 |
| P2 | Wrong among released test answers, and its exact one-sided 95% upper bound | both at most 10% |
| P4 | Evidence entries behind released answers reproduce live (`scripts/recheck_receipts.py`) | at least 99% |
| P5 | Test tasks answered | at least 50% of 333 |

Round 3 counts as a replication if P1, P2 and P4 are met. P3 was the gate's mechanism outcome; it became
the secondary hypothesis below when G2 failed.

**Secondary hypothesis H (test half, tested once).** Take the unanimous answers of best region, case routing
and transfer count. Those the pinned gate holds back are wrong more often than those it passes, by a
one-sided Fisher exact test at p < 0.05. The same test is reported on all six row-computed types. Also
reported, without certification:

- the chosen rule with the gate added on those three types: coverage, risk and its bound;
- the gate with runs 1 and 2, or run 1 alone, on those types: coverage, risk and runs per task.

Secondary outcomes, all reported:

- **S1.** The chosen rule against round 2's six rules on the same runs.
- **S2.** The own-level gate against the pinned gate.
- **S3.** Declared, allowed and pinned readings.
- **S5.** The chance control.
- **S6.** ReAct through the same chain.
- **S7.** Round 2's chosen rule, frozen and applied unchanged: does a certificate earned on CRMArena-Pro hold
  here?
- **S8.** How often the readings' answers contain the key, and the reading tables of withheld answers.
- **S9.** Key-reproduction flags and the blinded audit.
- **S10.** The standard report: an always-None baseline, the risk-coverage curve, errors per type, pass^3,
  cost and latency.

S4, readings proposed by the model, is not run. That is a limitation: the declared catalog is not compared
with model-generated readings.

## Budget and stop rules

- **Planned spend, at list price:**
  - calibration: crmroute $31 and ReAct $22;
  - test: crmroute $32 and ReAct $23;
  - with D1, about $122 of round 3's $169.
- **Price before calibration.** D1's routed price, $0.0276 per task, is under the +25% stop line, so ReAct
  stays on the calibration half.
- **Price after calibration.** The test cost is projected from calibration's measured price per task. If the
  projected total passes $169, ReAct is dropped from the test half. If it still passes $169, the round stops
  and the test half stays fresh.
- **Deadline.** Nothing launches after 2026-12-20, because Gemini 3.8 Flash's list price doubles on
  2027-01-01.
- **Resumes.** Runs that end in API errors are resumed with identical manifest pins and are never edited.
  Every redo is reported.

## Audit

The audit is fixed in advance:
- every wrong released test answer;
- a seeded random sample of right released answers at least as large;
- every key-reproduction flag.

Readers see the question, read-only org access, the receipts and two candidate answers in random order,
without being told which is the key. They give each item one of four labels: key wrong; ambiguous, with both
readings defensible; crmroute wrong; or unsure. The owner reads; a second reader, with Cohen's kappa, is added
only if one is found. The certificate is reported against the shipped key (primary) and against the audit
(secondary). The audit never feeds back into a rule.

## What will not be claimed

- **Not "first", "certified correct" or "guaranteed".** The risk bound is relative to the benchmark's key,
  holds under exchangeability between the two halves of one task pool, and covers this org only.
- **No benefit from the gate,** unless hypothesis H holds, and then only on its three types.
- **Not real-world performance.** These are benchmark orgs with templated questions and one model family.
  There are no real users, and no stakeholder interviews were conducted.
