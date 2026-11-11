# Reproduce it

Set up the agent, its servers and the benchmark, then rerun any experiment. Every command here produced a file in [`results/`](../results/); the raw run records are published as release assets, so the summaries can also be rebuilt without rerunning anything.

## Setup

Requirements: Node 22+, [uv](https://docs.astral.sh/uv/), Docker, [Ollama](https://ollama.com) with `qwen3:8b`,
a Groq key (Prompt Guard 2), and either a Google Cloud project with Vertex AI or a Gemini AI Studio key. Git LFS
is optional (only for CRMArena's released results).

```bash
# 0. keys: copy .env.example to .env at the repo root and fill it in (never commit it).
#    Vertex: GOOGLE_GENAI_USE_VERTEXAI=TRUE, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION=global,
#    VERTEXAI_PROJECT/_LOCATION for LiteLLM, and `gcloud auth application-default login`.

# 1. benchmark (own environment: it pins old libraries)
git clone https://github.com/SalesforceAIResearch/CRMArena vendor/CRMArena
cd vendor/CRMArena && git checkout $(cat ../../patches/crmarena-base-commit.txt) \
  && git apply ../../patches/crmarena-crmroute.patch
uv venv --python 3.11 .venv && uv pip install --python .venv -r ../../patches/crmarena-requirements.txt \
  && uv pip install --python .venv -e . --no-deps
cp ../../.env.example .env   # keep only the SALESFORCE_* lines, filled from the CRMArena README on GitHub
                             # (upstream rotates them; the pinned commit's copy can be out of date)
cd ../..

# 2. servers and agent
(cd mcp-salesforce && npm ci && npm run build)
(cd search && uv sync)
(cd agent && uv sync)

# 3. data: knowledge export + index, agent assets (schema text, router examples)
vendor/CRMArena/.venv/Scripts/python scripts/export_knowledge.py            # bin/python on Linux/macOS
search/.venv/Scripts/crm-knowledge-index --knowledge-dir data/knowledge --qdrant-path data/qdrant
vendor/CRMArena/.venv/Scripts/python scripts/export_agent_assets.py

# 4. local demo: agent :8000 (ADK web UI /dev-ui/), MCP :3333 and :8765, fallback on
./scripts/dev_up.sh
```

**Docker.** `docker build -t crmroute:local .` builds one image with the agent and both MCP servers (the
knowledge index is built into it). `scripts/run_systems.sh` runs it with the keys and Salesforce logins as env
files and mounts the gcloud credentials read-only for Vertex. On Windows with Smart App Control on, Windows
blocks spaCy's compiled parser, so on the host the guard falls back to pattern-only PII detection; measured runs
use the Docker image, where Presidio loads fully.

**Deployment.** Local only: `./scripts/dev_up.sh` or the Docker image. The project runs against Vertex AI from a
local machine; I dropped an earlier Cloud Run deployment and removed its unused agents-cli Terraform scaffold.

## Run the benchmark

`scripts/run_systems.sh` sets everything that must match across systems once: one pinned model per role (never
switched during a run), thinking level `low`, eval mode `aided` (every system gets the same task context), the
judge and simulated-user models, and the task ids. Each system and stream writes `manifest_<system>_<stream>.json`
once, with every pin plus hashes of the task list, routing table, harness patch, source tree and the image id; a
resume with any changed pin stops before a container starts or a model is called.

```bash
export BIG_MODEL=gemini-3.8-flash SMALL_MODEL=gemini-3.1-flash-lite POLICY_MODEL=gemini-3.1-flash-lite \
       CRMARENA_JUDGE_MODEL=ollama_chat/qwen3:8b CRMARENA_JUDGE_PROVIDER=ollama_chat \
       CRMARENA_USER_MODEL=ollama_chat/qwen3:8b CRMARENA_USER_PROVIDER=ollama_chat CRMARENA_THINKING_LEVEL=low

# dev: both solvers on the same dev tasks (streams per org can run side by side)
SPLIT=dev TASK_IDS=data/dev_run.json OUT=runs/dev3 ORGS=b2b PORT_OFFSET=0  ./scripts/run_systems.sh full agent_small
SPLIT=dev TASK_IDS=data/dev_run.json OUT=runs/dev3 ORGS=b2c PORT_OFFSET=10 ./scripts/run_systems.sh full agent_small
python scripts/fit_routing.py --big runs/dev3/full --small runs/dev3/agent_small --dev-split data/dev_run.json

# test, once: the four systems
SPLIT=test OUT=runs/test ORGS=b2b PORT_OFFSET=0  ./scripts/run_systems.sh react react_privacy full routed
SPLIT=test OUT=runs/test ORGS=b2c PORT_OFFSET=10 ./scripts/run_systems.sh react react_privacy full routed

python scripts/analyze_results.py --system react=runs/test/react --system react_privacy=runs/test/react_privacy \
  --system full=runs/test/full --system routed=runs/test/routed --baseline react \
  --task-ids data/test.json --big-model 3.8-flash --out results/test_summary.md
python scripts/make_results_figure.py   # the README's results figure, from results/test_summary.md

# a later change, measured on tasks no earlier step used: the measured and the changed image, same tasks
python scripts/make_fresh_split.py --out data/fresh.json   # commit it before any run
SPLIT=fresh TASK_IDS=data/fresh.json OUT=runs/fresh_before IMAGE=crmroute:local ./scripts/run_systems.sh routed
SPLIT=fresh TASK_IDS=data/fresh.json OUT=runs/fresh_after  IMAGE=crmroute:fixed PORT_OFFSET=20 ./scripts/run_systems.sh routed
python scripts/fresh_analysis.py --before runs/fresh_before/routed --after runs/fresh_after/routed --task-ids data/fresh.json

# the cap, false-refusal, router-overlap and spend checks over all of the above
python scripts/robustness_checks.py --out results/robustness_checks.md

# an org crmroute was not built on (the original CRMArena org): its splits, schema, router examples and index
vendor/CRMArena/.venv/Scripts/python scripts/make_org_split.py && vendor/CRMArena/.venv/Scripts/python scripts/add_org.py --org original
vendor/CRMArena/.venv/Scripts/python scripts/export_knowledge.py --orgs original && docker build -t crmroute:org .
export ROUTER_EXAMPLES=router_examples.jsonl,router_examples_original.jsonl
SPLIT=dev  TASK_IDS=data/original_dev.json  OUT=runs/original_dev  IMAGE=crmroute:org ORGS=original MODES=single ./scripts/run_systems.sh full agent_small
python scripts/fit_routing.py --org original --big runs/original_dev/full --small runs/original_dev/agent_small \
  --dev-split data/original_dev.json --test-split data/original_test.json --out agent/app/data/routing_original.yaml
SPLIT=test TASK_IDS=data/original_test.json OUT=runs/original_test IMAGE=crmroute:org ORGS=original MODES=single \
  ROUTING_TABLE=agent/app/data/routing_original.yaml ./scripts/run_systems.sh react full routed

# checkable answers (docs/checkable_answers.md): splits, then per split two routed runs and one 3.8 Flash run
vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --out-dir data --seed 20261031
vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --extend-calibration 4 --seed 20261101
export IMAGE=crmroute:checkable   # commit the splits before any run
for s in calibration test; do
  m=single; [ $s = test ] && m="single multi"   # the multi-turn test tasks: routed run 1 only
  SPLIT=checkable_$s TASK_IDS=data/checkable_$s.json OUT=runs/checkable_$s/r1 MODES="$m" PORT_OFFSET=100 ./scripts/run_systems.sh routed
  SPLIT=checkable_$s TASK_IDS=data/checkable_$s.json OUT=runs/checkable_$s/r2 MODES=single PORT_OFFSET=110 ./scripts/run_systems.sh routed
  SPLIT=checkable_$s TASK_IDS=data/checkable_$s.json OUT=runs/checkable_$s/f1 MODES=single PORT_OFFSET=120 ./scripts/run_systems.sh full
  # the baseline, ReAct with the privacy prompt, once: four streams (they can run side by side), read as one run
  python scripts/split_halves.py data/checkable_$s.json runs/checkable_splits/$s
  for h in 1 2; do for org in b2b b2c; do
    SPLIT=checkable_$s TASK_IDS=runs/checkable_splits/${s}_h$h.json OUT=runs/checkable_$s/react_h$h ORGS=$org MODES="$m" \
      ./scripts/run_systems.sh react_privacy
  done; done
done
python scripts/checkable_report.py --stage calibration   # certify the rules; commit them before reading any test result
vendor/CRMArena/.venv/Scripts/python scripts/recheck_receipts.py --runs runs/checkable_test/r1/routed \
  runs/checkable_test/r2/routed runs/checkable_test/f1/full --task-ids data/checkable_test.json --out runs/checkable_test/recheck.json
python scripts/checkable_report.py --stage test          # results/checkable_answers.md

# round 2 (docs/checkable_answers.md, "Round 2"): every remaining single-turn business task, the same image and runs
vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --round2 --seed 20261102
for s in calibration test; do
  SPLIT=checkable2_$s TASK_IDS=data/checkable2_$s.json OUT=runs/checkable2_$s/r1 MODES=single PORT_OFFSET=200 ./scripts/run_systems.sh routed
  SPLIT=checkable2_$s TASK_IDS=data/checkable2_$s.json OUT=runs/checkable2_$s/r2 MODES=single PORT_OFFSET=210 ./scripts/run_systems.sh routed
  SPLIT=checkable2_$s TASK_IDS=data/checkable2_$s.json OUT=runs/checkable2_$s/f1 MODES=single PORT_OFFSET=220 ./scripts/run_systems.sh full
  for org in b2b b2c; do
    SPLIT=checkable2_$s TASK_IDS=data/checkable2_$s.json OUT=runs/checkable2_$s/react ORGS=$org MODES=single ./scripts/run_systems.sh react_privacy
  done
done
# slow streams were shared out mid-run: their unfinished tasks (runs/checkable2_splits/*.json) ran with the same
# pins into react_p1..p6 and f1x, and the report reads each run's directories together (results/checkable_notebook.md)
python scripts/checkable2_report.py --stage calibration   # commit results/checkable2_rules.json before any test result
vendor/CRMArena/.venv/Scripts/python scripts/recheck_receipts.py --runs runs/checkable2_test/r1/routed \
  runs/checkable2_test/r2/routed runs/checkable2_test/f1/full,runs/checkable2_test/f1x/full \
  --task-ids data/checkable2_test.json --out runs/checkable2_test/recheck.json
python scripts/checkable2_report.py --stage test          # results/checkable2_answers.md

# round 3 (docs/checkable3_plan.md): the original org's 660 unused single-turn tasks, round 2's image unchanged;
# the chain and pinned readings were frozen first from development run D1 (docs/checkable3_devlog.md)
vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --round3 --seed 20261103
export ORGS=original MODES=single ROUTING_TABLE=agent/app/data/routing_original.yaml \
  ROUTER_EXAMPLES=router_examples.jsonl,router_examples_original.jsonl
run3() {  # split
  SPLIT=checkable3_$1 TASK_IDS=data/checkable3_$1.json OUT=runs/checkable3_$1/r1 PORT_OFFSET=330 ./scripts/run_systems.sh routed
  SPLIT=checkable3_$1 TASK_IDS=data/checkable3_$1.json OUT=runs/checkable3_$1/r2 PORT_OFFSET=340 ./scripts/run_systems.sh routed
  SPLIT=checkable3_$1 TASK_IDS=data/checkable3_$1.json OUT=runs/checkable3_$1/f1 PORT_OFFSET=350 ./scripts/run_systems.sh full
  SPLIT=checkable3_$1 TASK_IDS=data/checkable3_$1.json OUT=runs/checkable3_$1/react ./scripts/run_systems.sh react
  for r in "" _react; do  # the convention check: each answer's query re-run live under every date reading
    vendor/CRMArena/.venv/Scripts/python scripts/rewrite_recheck.py --records checkable3_$1$r --out runs/checkable3_$1/rewrites$r.jsonl
  done
}
run3 calibration
python scripts/checkable3_report.py --stage calibration   # commit results/checkable3_rules.json before the test half runs
run3 test
vendor/CRMArena/.venv/Scripts/python scripts/recheck_receipts.py --runs runs/checkable3_test/r1/routed \
  runs/checkable3_test/r2/routed runs/checkable3_test/f1/full --task-ids data/checkable3_test.json --out runs/checkable3_test/recheck.json
python scripts/checkable3_report.py --stage test          # results/checkable3_answers.md
python scripts/checkable3_secondary.py                    # results/checkable3_secondary.md
vendor/CRMArena/.venv/Scripts/python scripts/dev/checkable3_review.py pull   # the non-blind review, read-only
vendor/CRMArena/.venv/Scripts/python scripts/dev/checkable3_review.py report
```

`scripts/estimate_budget.py` projects a run's list-price cost from measured checkpoints before it starts. For
the judge check, `python scripts/judge_agreement.py sheet ...` writes a blind 40-item sheet; after labelling,
`... kappa` must reach κ ≥ 0.7.
