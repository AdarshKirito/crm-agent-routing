# How it was evaluated

The method behind every number: systems, splits, statistics, cost accounting, the harness patch, tests and CI, and tracing. Commands to rerun everything are in [reproduce.md](reproduce.md).

## Method

- Four systems, everything else fixed. 1: the benchmark's ReAct agent on `BIG_MODEL`; 2: the same agent with
  `--privacy_aware_prompt true`; 3: crmroute with every task on the big model (`CRMROUTE_MODE=no_route`);
  4: crmroute with the routing table. Same model per role, thinking level, eval mode, judge, simulated user and
  task ids for all four.
- Same inputs. Every system gets the same task context from the benchmark (eval mode `aided`) and the same
  customer-facing or internal flag per task. The prompts differ: ReAct uses the benchmark's own prompts,
  crmroute its own with the hints tuned on dev.
- Fixed, disjoint splits. `data/dev.json` and `data/test.json` (seed 20260927) are disjoint per org across both
  modes. All tuning used dev; the test set was run once, after the agent was frozen. Later, the hints ablation
  reran system 3 on the test tasks with the hints off, an analysis that changed nothing in the agent. The
  router's examples come from non-test tasks only.
- Statistics. 95% confidence intervals by bootstrap (5,000 resamples); systems are compared on the same task
  ids, and a difference is claimed only when the paired interval excludes zero.
- Cost. List prices applied to every response's usage metadata (cached and thinking tokens included), for every
  model call, including the guard's policy classifier and Prompt Guard, not only the solver.
- Pinned, resumable runs. Each system and stream writes a manifest with every pin plus hashes of the task list,
  routing table, harness patch, source tree and image id; a resume with any changed pin is refused.
- Live data. Every system queries the benchmark's own Salesforce orgs; nothing is mocked. ReAct queries them
  directly through the benchmark's connector. crmroute goes through its MCP server, which caches responses on
  disk for seven days because the shared orgs cap daily API calls, so a repeated query gets the earlier live
  response.
- Records. The run records (task records, harness configs, run manifests and per-call logs) are five release
  assets:
  - [run-records-2026-10-11](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-10-11):
    every run from the 2026-09-29 pilot to the original-CRMArena test, the test set included;
  - [run-records-2026-10-30](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-10-30):
    the hints ablation;
  - [run-records-2026-11-01](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-11-01),
    [run-records-2026-11-01-round2](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-11-01-round2)
    and [run-records-2026-11-05-round3](https://github.com/AdarshKirito/crm-agent-routing/releases/tag/run-records-2026-11-05-round3):
    the three rounds of checkable answers, receipts included.

  Extracted at the repository root they recreate `runs/`, and every summary in `results/` that comes from them
  rebuilds row for row. Server and container logs are not published.

<details>
<summary><b>Dev: tuning and the routing fit</b></summary>

Everything here is on dev tasks only (`data/dev_run.json`: all 220 dev single-turn tasks plus 20 of the 76 dev
multi-turn tasks, one per task type and org), with the same pins as the test run.

- Tuning (`results/dev_tuning.md`). A diagnostic dev run found rules the agent got wrong, and I checked each one
  against the live orgs on several dev tasks before it became a hint. The fixes: relative periods must end at the
  task's "today"; an empty, correctly filtered query means None; the answer-key conventions for monthly trends,
  activity priority, wrong stage, sales amount and sales cycle; the policy articles to check for quote approval
  and invalid configuration; short answers for free-text tasks; when to ask clarifying questions in a
  conversation; the customer's own identity in conversations; one guard false refusal. On the same business
  single-turn dev tasks, Flash-Lite went from 57.9% to 64.2% (190 tasks) and 3.8 Flash from 52.0% to 61.0% (the
  100 it had reached when the diagnostic run was stopped).
- Final dev run (`results/dev_summary.md`, frozen agent, complete, no API errors):

  | agent on | business single-turn (n=190) | business multi-turn (n=20) | refusals (n=30) | $/business task |
  |---|---|---|---|---|
  | Gemini 3.8 Flash | 70.5% [63.7, 76.8] | 40.0% [20.0, 60.0] | 30/30 | 0.0429 |
  | Gemini 3.1 Flash-Lite | 64.2% [57.4, 71.1] | 50.0% [30.0, 70.0] | 30/30 | 0.0081 |

- Routing fit (`agent/app/data/routing.yaml`, `--margin 2 --min-n 8`): 9 of 19 business task types go to
  Flash-Lite (activity priority, invalid configuration, lead qualification, lead routing, named-entity
  disambiguation, sales amount, sales insight mining, top issue, wrong stage); the rest stay on 3.8 Flash. With
  about 11 dev tasks per type, each per-type rate is noisy, so the fit is a cost decision checked on test, not a
  claim about each type.

</details>

<details>
<summary><b>What the CRMArena patch changes</b> (<code>patches/crmarena-crmroute.patch</code>)</summary>

- a `remote` agent strategy that drives an ADK server and hands the benchmark only the agent's replies;
- Gemini 3.x on Vertex AI (`vertex_ai/...`) and the AI Studio key (`gemini/...`), plus `mistral`, `groq`,
  `openrouter` and `ollama_chat`; Gemini 3 gets one shared setting (temperature 1.0, fixed `thinking_level`,
  output budget);
- configurable judge and simulated-user models (temperature 0 for a non-Gemini judge);
- one rate-limit-aware completion wrapper for the agent, judge and simulated user: it waits and retries the
  same model on 429/503 and connection errors, stops the run on a used-up daily quota, and logs the model
  that answered every call, with its list-price cost (unknown prices stay unknown, never $0);
- a request above 250K input tokens is not sent: the task counts as the system's failure (reward 0, as
  upstream scores exceptions). On the free tier that is the per-minute quota; on Vertex it caps runaway
  ReAct contexts, which grow by every observation. Only ReAct reached it (17 test tasks; see
  `results/robustness_checks.md` for what it does to the comparison);
- resumable runs with pinned configuration: each checkpoint has a `config_*.json` with every pin and a hash
  of the selected tasks; a resume with different pins is refused; checkpoints are written atomically and
  keep earlier failed attempts; `run_tasks.py` exits non-zero while any selected task lacks a completed
  execution, and stops after 3 errors in a row;
- only malformed-query errors go back to the solver; DNS, login and quota errors propagate so the task is
  redone on resume;
- `--task_ids_file` for fixed task lists, and `--dry_run`;
- fixes for upstream bugs: a missing `import re` in the grader's fallback parser, a crash on SOSL results that
  mix object types, the simulated user's cost being overwritten instead of summed, an unrecorded extra
  simulated-user call, and the evaluator mishandling the original CRMArena's single answers (those tasks store
  one answer, not a list: string answers never matched, a None answer raised an error, and fuzzy answers were
  compared with their first character);
- the agent's last answer check copied into the run record next to its guard and route;
- JSON code fences stripped before the grader parses them; LiteLLM ≥ 1.84, never 1.82.7/1.82.8 (the measured
  runs used 1.103).

</details>

## Tests and CI

| suite | what it covers | result |
|---|---|---|
| `mcp-salesforce` (`npm test`) | SOQL/SOSL guards (incl. locking clauses), Id checks, cache scoping, shared in-flight reads, atomic disk writes, pagination caps, response budget, `--env` start-up | 17 passed |
| `mcp-salesforce` live smoke (`npx tsx test/smoke.ts --env ...`, run by hand) | all 5 tools on both live orgs via the official MCP client; write attempts and unknown orgs rejected | passed |
| `agent` (`uv run pytest`) | guard (ownership filters, knowledge filtering on every read, identity in conversations), checker, PII scrub, Prompt Guard parsing and accounting, cost accounting, pinned retry vs fallback on real provider errors, tool-call repair, tracing export, the real ADK graph offline with a scripted model, fail-closed classifier, checker abstention, router examples from several files, the task-hints switch, tool-call receipts (budget and blocked calls included), receipt checks, the receipt-guided retry, the round-3 derivations of six task types | 98 passed, 11 live tests skipped without their env flags |
| `search` fork (`uv run pytest`) | upstream behaviour plus the knowledge index: mode-specific embedding, org isolation, response budget | 36 passed |
| `tests/` (benchmark env) | harness retries, resume pins, atomic checkpoints, adapter failure handling, run manifests, complete-split analysis, routing fit pairing, judge-agreement binding, budget estimate, scoring the original org's single answers, released runs that reuse task ids, round 3's convention readings, gate, release rules, rewrite re-check and report, and `checkable` against the code it was ported from | 85 passed, 1 live test skipped |
| `checkable` (`python -m pytest`) | date readings, receipts and their re-check, the reading check and learned conventions, release rules and the Learn-then-Test certificate | 16 passed |

CI (`.github/workflows/ci.yml`) runs the offline suites (every row except the live smoke test; `checkable` on
Python 3.10, with its demo) on every push to `main` and every pull request, and rebuilds the patched benchmark from the pinned upstream commit to prove the
patch still applies. The PR eval (`.github/workflows/eval-pr.yml`) runs 15 fixed dev cases on Flash-Lite and
fails if business success falls more than one case below `evals/ci_baseline.json` (7 of 12), if a refusal is
missed (3 of 3), or if task ids or model/judge pins change. It runs on pull requests that touch the agent, the
servers, the patch or the evals when the repository variable `CRMROUTE_PR_EVAL=true` is set, or by manual
dispatch. It ran twice by manual dispatch (one failure, then a pass), then on its first pull request,
[#1](https://github.com/AdarshKirito/crm-agent-routing/pull/1), which it passed with 10 of 12 business cases and
3 of 3 refusals (that PR leaves the agent's behaviour unchanged, so the gain over the baseline's 7 is not an
improvement it made). It passed again on [#2](https://github.com/AdarshKirito/crm-agent-routing/pull/2) (10 of 12,
3 of 3), [#4](https://github.com/AdarshKirito/crm-agent-routing/pull/4) (9 of 12, 3 of 3) and
[#5](https://github.com/AdarshKirito/crm-agent-routing/pull/5) (7 of 12, 3 of 3; that PR's two changed cases
were run-to-run variation, and every knowledge search it made returned the same articles as before). On #4 it first
failed twice without running a case: the Gemini key had expired, and then the replacement key's project had no
credits. It needs two repository secrets (`GEMINI_API_KEY`, `GROQ_API_KEY`); the Salesforce logins are the
benchmark's public demo-org credentials, read from the README on CRMArena's default branch because upstream
rotates them (the harness code stays at the pinned commit).

## Tracing

With tracing on, every request is one trace in [Arize Phoenix](https://github.com/Arize-ai/phoenix): the workflow
nodes, each model call and each MCP tool call, with token counts. Run `uvx --from arize-phoenix phoenix serve`
and start the agent with `PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006` (from Docker:
`http://host.docker.internal:6006`).

![Phoenix trace of dev task b2c/1943](img/phoenix_trace.png)

This is dev task b2c/1943 on Gemini 3.8 Flash, a customer asking for a product they bought: intake → screen →
policy_check → decide → route_task → solver (its model calls and SOQL queries) → check → finalize. The query
marked red is a nested orders-with-items query that the tool guard rejects in a customer session; the agent then
made separate queries scoped to the customer's own account. p95 latency, tool errors and tool steps per task for
the measured runs come from the run records (`scripts/analyze_results.py`), not from Phoenix.
