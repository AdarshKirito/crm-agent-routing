# crmroute agent

The ADK 2.10 `Workflow` behind crmroute: guard → router → solver → checker. The project overview,
results and full setup are in the [main README](../README.md).

## Layout

```
agent/
├── app/
│   ├── agent.py          # builds the Workflow graph
│   ├── nodes.py          # function nodes: intake, screen, policy check, decide, refuse, route_task, check, finalize
│   ├── models.py         # one pinned model per role (retries on the same model); demo-only fallback
│   ├── guard/            # Presidio, sensitive-field map, policy, Prompt Guard 2, tool-call guard
│   ├── router.py         # nearest-neighbour task-type vote (no LLM call)
│   ├── checker.py        # Ids in tool evidence, answer form, one retry
│   ├── task_specs.py     # per-task hints tuned on dev
│   ├── prompts.py
│   ├── tools.py          # McpToolset connections to the two MCP servers
│   ├── usage.py          # logs and prices every model call
│   ├── tracing.py        # Phoenix / OpenTelemetry export
│   ├── fast_api_app.py   # ADK API server (also serves the ADK web UI at /dev-ui/)
│   └── data/             # routing table, router examples, schema text
└── tests/                # unit and integration tests (offline by default)
```

## Run

```bash
uv sync
uv run pytest                      # unit + integration; live tests are skipped without their env flags
uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
```

The agent expects the Salesforce MCP server at `CRMROUTE_SALESFORCE_MCP_URL` (default
`http://127.0.0.1:3333/mcp`) and the knowledge search server at `CRMROUTE_SEARCH_MCP_URL` (default
`http://127.0.0.1:8765/mcp`); `../scripts/dev_up.sh` starts all three. Models and keys come from the
repo-root `.env` (see `../.env.example`).

Scaffolded with `agents-cli` 1.7.0; files that keep a Google LLC Apache-2.0 header come from that scaffold.
