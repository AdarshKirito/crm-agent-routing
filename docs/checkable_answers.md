# Checkable answers

crmroute gives a CRM answer only when the answer can be checked, and otherwise withholds it. This page
describes the method and how it is evaluated. Results are in `results/checkable_answers.md` once the
final test has run; every trial along the way is in `results/checkable_notebook.md`.

## The property

For every business question crmroute answers:

1. **The answer has a receipt.** Every tool call of the session is recorded with its arguments (the SOQL
   or SOSL text), its status (ok, error, blocked by the confidentiality policy, or refused because the tool
   budget was used up), the row counts the Salesforce server reports and the result exactly as the model
   saw it (`agent/app/receipts.py`). The benchmark harness copies the receipt into each task record.
2. **Code checks the answer against its receipt** (`agent/app/receipt_check.py`, standard library only).
   The answer is parsed in the form its task type expects. An answer cannot be shown from its receipt when
   it names an Id no tool result holds, rests on no tool result at all, does not parse, or declines or
   abstains instead of answering. Softer signals are recorded too: the tool budget ran out, tool errors,
   policy blocks, a "None" with no empty query result behind it, an Id seen only in cut-off results, an Id
   the question names that no query used, and a question about a period whose supporting queries have no
   date filter.
3. **A release rule decides, and its risk is certified.** The rule sees only what a deployment would see:
   the receipt checks, whether independent runs of the agent agree, and the router's predicted task type
   (never the true type or the answer key). It is chosen on a calibration split with Learn-then-Test
   (fixed-sequence testing over rules in a pre-registered order, exact binomial p-values), so that the
   share of wrong answers among released answers stays at or below a target alpha with confidence
   1 - delta. Everything else is withheld and counted.
4. **Anyone can re-run the evidence.** `scripts/recheck_receipts.py` re-runs the queries an answer rests
   on against the benchmark's public orgs with simple_salesforce (not crmroute's server) and compares the
   live rows with the recorded ones.

The same code reads receipts rebuilt from the benchmark's ReAct agent (its trajectory keeps every query and
its output), so the baseline can be passed through the same checks and rule.

## Evaluation

- **Splits** (`data/checkable_*.json`, `scripts/make_checkable_splits.py`): CRMArena-Pro business tasks
  that no earlier split used and that are not router examples. Per org and task type: 4 practice tasks
  (building the rule), 12 calibration tasks (fitting it once the method is frozen; raised from 8 before
  any calibration run, for the power to certify) and 8 test tasks plus 2 multi-turn tasks (run once). No
  confidentiality task is unused, so refusals are only re-checked for regressions on earlier splits.
- **Systems:** crmroute (routed) run several times independently, and ReAct with the benchmark's privacy
  prompt run once at about the same list-price cost, with the same models, judge and simulated user.
- **Measures:** coverage (answers given / tasks), risk (wrong answers / answers given) with an exact upper
  bound, the standard benchmark score (a withheld answer scores as a failure), pass^k over the repeats,
  latency (one run, and the repeats in parallel), list-price cost, and the share of released answers whose
  evidence reproduces live.

## Pre-registration

Fixed before any calibration or test run, from the practice runs only (`results/checkable_notebook.md`).

**System.** crmroute, image `crmroute:checkable` 658df1a6bc7f (its agent code is that of commit
0121418, unchanged since), with the test run's pins (Gemini 3.8 Flash and 3.1 Flash-Lite on Vertex AI,
thinking low, aided mode, a local qwen3:8b judge and simulated user) and the receipt-guided retry off. Each task is answered by three independent
runs: two of the routed system and one with every task on 3.8 Flash (system 3), taken in that order when
repeats are added one at a time. Part 2 of this pre-registration, committed after practice round 3 and
before any crmroute calibration or test run. In practice, of the 76 answers three routed runs agreed on
cleanly, the 3.8 Flash run disagreed with 2 of the 5 wrong ones and 2 of the 71 right ones; over the three
ways of pairing it with two routed runs, the risk of the rules that need all three runs to agree fell from
6.6% to 4.1-5.3% at about the same coverage and list-price cost (`results/checkable_notebook.md`, round 3).
A modest, in-sample difference: the calibration and test runs measure it again. The baseline is the benchmark's ReAct agent with its privacy prompt, one run per task, on the
same models, judge and simulated user, its receipts rebuilt from its trajectories; its protocol below is
fixed by this commit.

**Splits.** Calibration: `data/checkable_calibration.json` (456 single-turn business tasks). Test:
`data/checkable_test.json` (304 single-turn and 76 multi-turn business tasks).

**Release procedure** (`scripts/release_eval.py` and `agent/app/receipt_check.py` at this commit). Answers whose predicted task type has a
free-text or BANT answer form are never released (`--withhold-forms text,bant`). The rule family, in this
order, strictest first: for an agreement level from all runs down to one, the agreeing runs show no
used-up budget, no unsupported None and no tool error; then no used-up budget and no unsupported None;
after those, the same agreement levels with no flag required. Target risk alpha = 0.10, delta = 0.10:
Learn-then-Test with fixed-sequence testing on the calibration runs, exact binomial p-values, chooses the
most permissive rule certified before the first failure. The chosen rule is committed before any test
result is read, then applied unchanged to the test runs. The baseline goes through the same procedure with
its one run.

**Primary outcomes** (single-turn test tasks, crmroute):

1. A rule is certified on the calibration split.
2. On the test split, the certified rule's share of wrong answers among released answers is at most
   10%; its exact 95% upper bound is reported beside it.
3. The certified rule answers at least 40% of the 304 single-turn test tasks.
4. At least 99% of the evidence entries behind released test answers reproduce live with
   `scripts/recheck_receipts.py` (exact rows; SOSL searches, which Salesforce ranks, by the answer's Ids).

**Reported either way:** crmroute against the baseline, each with its own certified rule, as paired
differences in coverage and in the standard score with 95% bootstrap intervals (a lead is claimed only if
the interval excludes zero); each run's standard benchmark score on the test split; pass^k over the
repeats; latency of one run and of the repeats in parallel; list-price cost with and without adaptive
repeats; the risk and coverage of crmroute's first run alone under the one-run part of the family,
certified on its own calibration run; a B2B-to-B2C check (calibrated on B2B calibration tasks only,
evaluated on B2C test tasks); and, uncertified and descriptive because conversations are a different
distribution, the rule certified for crmroute's first run alone and the baseline's certified rule, each
applied to one run of its system on the 76 multi-turn test tasks. Refusals of confidential requests are
re-checked on the old test split's 42 (`data/checkable_refusal_check.json`) for regressions.

## Round 2: a competence map (pre-registration)

Round 1's results are in `results/checkable_answers.md`. Fixed before any round-2 run, from round-1 records
only; no round-2 record is opened before the round-2 rules are committed.

**Why.** Round 1's records (all 912 tasks: practice, calibration and test) are now development data. In them,
most wrong answers that the looser rules release come from a few task types where every run makes the same
mistake: sales amounts summed under another definition than the answer key's, quote-configuration rules cited
for quotes the key finds valid, wrong opportunity stages. Agreement and receipts cannot see an error that
every run shares; a record of how often each kind of question went wrong before can. Scored on each round-1
split with the types chosen on the other two, withholding the predicted task types whose released answers
were wrong more than 20% of the time raised the three-run system's coverage from 38.6% to 54.4% at about the
same risk (6.0% and 6.2%). An LLM cross-check of the evidence was considered and left out: the answers it would
have to rescue (two of three runs agreeing) were wrong 57% of the time in round 1.

**System.** Unchanged from round 1: image `crmroute:checkable` 658df1a6bc7f, the same pins, three runs per
task (two routed, one with every task on 3.8 Flash). Baseline: ReAct with the privacy prompt, one run, same
models, judge and simulated user.

**Splits.** `data/checkable2_calibration.json` (410 tasks) and `data/checkable2_test.json` (431): every
CRMArena-Pro business single-turn task that no earlier split or router example used, halved at random per org
and type (`scripts/make_checkable_splits.py --round2 --seed 20261102`). They are the benchmark's last unused
tasks, so the type mix follows what is left (13 to 26 per org and type), not round 1's balanced design.

**Release procedure** (`round2_rules` and `calibrate_widest` in `scripts/release_eval.py` at this commit). For
a system with k runs per task, a competence map withholds the predicted task types whose answers the same
rule released in that system's round-1 runs were wrong more than a threshold of the time; free-text and BANT
answers are never released. The chain, in order: with the 15% map, all k runs agree and show no used-up
budget, unsupported None or tool error; then no used-up budget or unsupported None; then no flag required;
then the same three with the 20% map. Learn-then-Test on the round-2 calibration runs (fixed-sequence
testing, exact binomial p-values, alpha = delta = 0.10). Of the rules certified before the first failure, which
all hold their bound together, the one that answers the most calibration tasks is chosen, committed before
any round-2 test result is read and applied unchanged to the round-2 test runs. The same procedure runs for
crmroute's first run alone and for the baseline (k = 1; each map from that system's own round-1 runs; the
baseline uses the router types of crmroute's first run).

**Primary outcomes** (crmroute, three runs, the 431 round-2 test tasks):

1. A rule of the chain is certified on the round-2 calibration split.
2. Its share of wrong answers among released test answers is at most 10%.
3. Its exact one-sided 95% upper bound on that share is at most 10% (round 1: 12.4%).
4. It answers at least 50% of the test tasks (round 1: 40.5%).
5. At least 99% of the evidence entries behind released test answers reproduce live.
6. It answers more test tasks than round 1's certified rule applied to the same test runs, and more than the
   baseline under its own round-2 rule; for each, the paired 95% bootstrap interval of the coverage
   difference excludes zero.

**Reported either way:** the chain on calibration for each system; for each chosen rule on test its coverage,
risk, upper bound and standard score, by task type; the paired standard-score differences; repeats, latency
and list-price cost, with and without adaptive repeats; and each run's standard benchmark score on the
round-2 test split.
