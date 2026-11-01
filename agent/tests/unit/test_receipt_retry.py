import json

from app import nodes
from app import state_keys as K


def _state(*entries):
    return {K.CONVERSATION: [{"role": "user", "text": "Which issue was reported most for product 01tWt000006hV58IAE?"}],
            K.RECEIPT: list(entries)}


def _entry(n, rows, status="ok"):
    payload = {"totalSize": len(rows), "returned": len(rows), "truncated": False, "records": rows}
    return {"n": n, "turn": 1, "tool": "soql_query", "args": {"query": "SELECT ..."}, "status": status,
            "totalSize": len(rows), "result": json.dumps(payload)}


def test_off_by_default(monkeypatch):
    monkeypatch.setattr(nodes, "RECEIPT_RETRY_CALLS", 0)
    assert nodes.receipt_feedback("answer", "None", "id", _state(_entry(1, [{"Id": "a03Wt00000JqvNUIAZ"}]))) == []


def test_unsupported_none_and_used_up_budget_get_feedback(monkeypatch):
    monkeypatch.setattr(nodes, "RECEIPT_RETRY_CALLS", 4)
    rows = _entry(1, [{"Id": "a03Wt00000JqvNUIAZ"}])
    budget = {"n": 2, "turn": 1, "tool": "soql_query", "args": {}, "status": "budget", "result": "Tool budget used up"}
    [none_problem] = nodes.receipt_feedback("answer", "None", "id", _state(rows))
    assert "answered None" in none_problem
    problems = nodes.receipt_feedback("answer", "a03Wt00000JqvNUIAZ", "id", _state(rows, budget))
    assert len(problems) == 1 and "4 more calls" in problems[0]


def test_supported_none_refusals_and_questions_pass(monkeypatch):
    monkeypatch.setattr(nodes, "RECEIPT_RETRY_CALLS", 4)
    assert nodes.receipt_feedback("answer", "None", "id", _state(_entry(1, []))) == []
    assert nodes.receipt_feedback("refuse", "I cannot share this.", "id", _state()) == []
    assert nodes.receipt_feedback("clarify", "Which period?", "id", _state()) == []
    assert nodes.receipt_feedback("answer", "I refuse", "refusal", _state()) == []
