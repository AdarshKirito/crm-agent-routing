import json
from types import SimpleNamespace

import pytest

from app import state_keys as K
from app.config import MAX_TOOL_CALLS_PER_TURN
from app.guard.tool_guard import after_tool, before_tool


def test_model_output_cannot_become_its_own_checker_evidence():
    state = {K.AUDIENCE: "employee", K.EVIDENCE: "real tool result"}
    after_tool(SimpleNamespace(name="set_model_response"), {}, SimpleNamespace(state=state),
               {"kind": "answer", "answer": "005Wt000009ZZZZIAW"})
    assert state[K.EVIDENCE] == "real tool result"
    assert K.NOTES not in state


def test_failed_tool_result_is_not_checker_evidence():
    state = {K.AUDIENCE: "employee"}
    after_tool(SimpleNamespace(name="get_record"), {}, SimpleNamespace(state=state),
               {"isError": True, "content": [{"text": "No record for 005Wt000009ZZZZIAW"}]})
    assert "005Wt000009ZZZZIAW" not in state.get(K.EVIDENCE, "")
    assert "ERROR" in state[K.NOTES][0]


@pytest.mark.parametrize("name,args,payload", [
    ("soql_query", {"query": "SELECT Title, FAQ_Answer__c FROM Knowledge__kav"},
     {"records": [{"Title": "Volume-Based Discounts", "FAQ_Answer__c": "secret discount"}]}),
    ("sosl_search", {"query": "FIND {discount} RETURNING Knowledge__kav(Title, FAQ_Answer__c)"},
     {"records": [{"_type": "Knowledge__kav", "Title": "Volume-Based Discounts", "FAQ_Answer__c": "secret discount"}]}),
    ("get_record", {"object_name": "Knowledge__kav", "record_id": "ka0Wt0000001234IAA"},
     {"Title": "Volume-Based Discounts", "FAQ_Answer__c": "secret discount"}),
    ("search_knowledge", {"query": "discount"},
     {"articles": [{"Title": "Volume-Based Discounts", "FAQ_Answer__c": "secret discount"}]}),
])
def test_every_knowledge_tool_filters_confidential_text_and_structured_copy(name, args, payload):
    state = {K.AUDIENCE: "customer"}
    result = after_tool(SimpleNamespace(name=name), args, SimpleNamespace(state=state),
                        {"content": [{"type": "text", "text": json.dumps(payload)}], "structuredContent": payload})
    assert result is not None
    assert "secret discount" not in json.dumps(result)
    assert "secret discount" not in state.get(K.EVIDENCE, "")


def test_missing_article_title_is_withheld_and_public_article_kept():
    state = {K.AUDIENCE: "customer"}
    result = after_tool(SimpleNamespace(name="soql_query"), {"query": "SELECT Id, Title FROM Knowledge__kav"},
                        SimpleNamespace(state=state), {"content": [{"text": json.dumps({"records": [
                            {"FAQ_Answer__c": "unclassifiable secret"}, {"Title": "Product care", "Summary": "public"},
                        ]})}]})
    assert "unclassifiable secret" not in json.dumps(result)
    assert "Product care" in json.dumps(result)


def test_malformed_knowledge_payload_is_blocked_without_crash():
    state = {K.AUDIENCE: "customer"}
    result = after_tool(SimpleNamespace(name="search_knowledge"), {}, SimpleNamespace(state=state),
                        {"content": [{"text": "[]"}]})
    assert result["isError"]
    assert K.EVIDENCE not in state


def _call(name, args, state, response=None):
    """One tool call as ADK runs it: before_tool may answer it itself; after_tool sees the result."""
    tool, ctx = SimpleNamespace(name=name), SimpleNamespace(state=state)
    response = before_tool(tool, args, ctx) or response
    return after_tool(tool, args, ctx, response) or response


def _rows(payload):
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def test_receipt_keeps_query_result_and_row_counts():
    state = {K.AUDIENCE: "employee", K.TURN: 1}
    query = "SELECT Id FROM Case WHERE Status = 'Closed'"
    _call("soql_query", {"query": query}, state,
          _rows({"totalSize": 3, "returned": 2, "truncated": True, "records": [{"Id": "500A"}, {"Id": "500B"}]}))
    [entry] = state[K.RECEIPT]
    assert entry["n"] == 1 and entry["turn"] == 1 and entry["tool"] == "soql_query"
    assert entry["args"] == {"query": query} and entry["status"] == "ok"
    assert (entry["totalSize"], entry["returned"], entry["truncated"]) == (3, 2, True)
    assert json.loads(entry["result"])["records"][1]["Id"] == "500B" and len(entry["sha256"]) == 64


def test_receipt_marks_errors_budget_and_policy_blocks():
    state = {K.AUDIENCE: "customer", K.TURN: 1}
    _call("soql_query", {"query": "SELECT Nme FROM Product2"}, state,
          {"isError": True, "content": [{"type": "text", "text": "No such column 'Nme'"}]})
    _call("soql_query", {"query": "SELECT Id, Name FROM User"}, state)  # internal object in a customer session
    state[K.TOOL_CALLS_TURN] = MAX_TOOL_CALLS_PER_TURN
    _call("soql_query", {"query": "SELECT Id FROM Product2"}, state)
    assert [e["status"] for e in state[K.RECEIPT]] == ["error", "blocked", "budget"]
    assert [e["n"] for e in state[K.RECEIPT]] == [1, 2, 3]


def test_receipt_records_knowledge_results_as_the_model_saw_them():
    state = {K.AUDIENCE: "customer", K.TURN: 1}
    _call("search_knowledge", {"query": "discount"}, state, _rows({"articles": [
        {"Title": "Volume-Based Discounts", "Summary": "internal"}, {"Title": "Product care", "Summary": "public"}]}))
    [entry] = state[K.RECEIPT]
    assert entry["status"] == "ok" and entry["withheld_confidential"] == 1
    assert "Product care" in entry["result"] and "Volume-Based Discounts" not in entry["result"]


def test_model_output_tool_is_not_a_receipt_entry():
    state = {K.AUDIENCE: "employee"}
    after_tool(SimpleNamespace(name="set_model_response"), {}, SimpleNamespace(state=state), {"kind": "answer"})
    assert K.RECEIPT not in state
