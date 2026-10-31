import json

from app import task_specs
from app.guard.sensitive import SF_ID_RE
from app.receipt_check import BANT, ID_RE, STAGES, Claim, check, parse_claim, same_answer, token_f1

AGENT = "005Wt000003NDqDIAW"
OTHER = "005Wt000003NDqEIAW"


def entry(n, result, status="ok", tool="soql_query", turn=1, **counts):
    return {"n": n, "turn": turn, "tool": tool, "args": {"query": "SELECT ..."}, "status": status,
            "result": json.dumps(result) if not isinstance(result, str) else result, **counts}


def test_id_pattern_and_vocabularies_match_the_agent():
    assert ID_RE.pattern == SF_ID_RE.pattern
    assert (STAGES, BANT) == (task_specs.STAGES, task_specs.BANT)


def test_value_answers_must_name_a_value_of_the_form():
    assert parse_claim("California", "state") == Claim("value", ("CA",))
    assert parse_claim("CA", "state") == Claim("value", ("CA",))
    assert parse_claim("Quote", "stage") == Claim("value", ("Quote",))
    assert parse_claim("<thought> Let's query: SELECT CreatedDate FROM Case", "month").kind == "unparsed"
    assert parse_claim("March or April", "month").kind == "unparsed"


def test_claims_by_answer_form():
    assert parse_claim(AGENT, "id") == Claim("ids", (AGENT,))
    assert parse_claim(" none. ", "id").kind == "none"
    assert parse_claim("November", "month") == Claim("value", ("November",))
    assert parse_claim("Budget, Authority", "bant").key() == ("value", ("authority", "budget"))
    assert parse_claim("I cannot share this information because it is confidential.", "text").kind == "refusal"
    assert parse_claim("I could not verify an answer from the CRM records, so I can't give one.", "id").kind == "abstain"
    assert parse_claim("the agent with the most cases", "id").kind == "unparsed"


def test_same_answer_compares_ids_by_15_characters_and_text_by_overlap():
    assert same_answer(parse_claim(AGENT, "id"), parse_claim(AGENT[:15], "id"))
    assert not same_answer(parse_claim(AGENT, "id"), parse_claim(OTHER, "id"))
    assert same_answer(parse_claim("Hybrid and electric vehicles", "text"), parse_claim("hybrid, electric vehicles", "text"))
    assert token_f1("luxury SUVs", "compact cars") == 0.0


def test_id_from_a_tool_result_is_grounded():
    verdict = check(AGENT, "id", [entry(1, {"totalSize": 1, "records": [{"OwnerId": AGENT}]}, totalSize=1)])
    assert verdict.ok and verdict.support == [1] and not verdict.flags


def test_id_seen_nowhere_is_ungrounded_unless_the_asker_gave_it():
    receipt = [entry(1, {"totalSize": 1, "records": [{"OwnerId": OTHER}]}, totalSize=1)]
    assert not check(AGENT, "id", receipt).ok
    assert check(AGENT, "id", receipt, context=f"Case owner: {AGENT}").ok


def test_errors_and_policy_blocks_are_not_evidence():
    receipt = [entry(1, f"INVALID_FIELD: {AGENT}", status="error"), entry(2, f"Blocked: {AGENT}", status="blocked")]
    verdict = check(AGENT, "id", receipt)
    assert verdict.flags["ungrounded"] == 1 and verdict.flags["no_data"] == 1
    assert verdict.flags["errors"] == 1 and verdict.flags["blocked"] == 1


def test_none_needs_an_empty_query_result_to_avoid_the_flag():
    rows = entry(1, {"totalSize": 2, "records": [{"Id": OTHER}]}, totalSize=2)
    empty = entry(2, {"totalSize": 0, "records": []}, totalSize=0)
    assert check("None", "id", [rows]).flags.get("none_without_empty") == 1
    assert "none_without_empty" not in check("None", "id", [rows, empty]).flags


def test_soft_flags_budget_and_cut_off_support():
    receipt = [entry(1, {"totalSize": 900, "returned": 200, "truncated": True, "records": [{"OwnerId": AGENT}]},
                     totalSize=900, returned=200, truncated=True),
               entry(2, "Tool budget used up (10 calls for this request).", status="budget")]
    verdict = check(AGENT, "id", receipt)
    assert verdict.ok
    assert verdict.flags["budget"] == 1 and verdict.flags["truncated_support"] == 1


def test_flags_count_only_the_final_turn_for_budget_and_errors():
    receipt = [entry(1, "bad query", status="error", turn=1),
               entry(2, {"totalSize": 1, "records": [{"Id": AGENT}]}, turn=2, totalSize=1)]
    verdict = check(AGENT, "id", receipt)
    assert verdict.ok and "errors" not in verdict.flags


def test_refusal_is_a_hard_flag():
    verdict = check("I cannot share this because it is confidential.", "text", [entry(1, {"articles": []})])
    assert not verdict.ok and verdict.flags["refusal"] == 1 and "no_data" not in verdict.flags
