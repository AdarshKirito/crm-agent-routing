"""Receipts: one entry per tool call, kept in session state.

Each entry records what was asked (the tool and its arguments, e.g. the SOQL text) and what came
back, exactly as the model saw it, with the row counts the Salesforce server reports. An answer
can then be traced to the read-only queries behind it and re-checked after the run.
"""

import hashlib
import json
from typing import Any

from . import state_keys as K

# The Salesforce server caps one response at 16,000 characters (SF_MAX_RESPONSE_CHARS).
MAX_RESULT_CHARS = 32_000
STATUSES = ("ok", "error", "blocked", "budget")  # blocked: confidentiality policy; budget: tool budget used up


def row_counts(text: str) -> dict[str, Any]:
    """The counts a query result reports ({totalSize, returned, truncated}), if it is one."""
    try:
        payload = json.loads(text)
    except ValueError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {k: payload[k] for k in ("totalSize", "returned", "truncated", "withheld_confidential") if k in payload}


def record(state: Any, tool: str, args: dict[str, Any], status: str, text: str) -> None:
    assert status in STATUSES, status
    receipt = list(state.get(K.RECEIPT) or [])
    receipt.append({
        "n": len(receipt) + 1,
        "turn": int(state.get(K.TURN) or 0),
        "tool": tool,
        "args": json.loads(json.dumps(args, default=str)),
        "status": status,
        **row_counts(text),
        "chars": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "result": text[:MAX_RESULT_CHARS],
    })
    state[K.RECEIPT] = receipt
