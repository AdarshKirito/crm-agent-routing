"""Round-3 rewriter: a receipt's date conditions are replaced by a reading's window, nothing else changes."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rewrite_recheck as RW

START, END = datetime(2023, 12, 1, tzinfo=timezone.utc), datetime(2024, 3, 1, tzinfo=timezone.utc)
WINDOW = "CreatedDate >= 2023-12-01T00:00:00Z AND CreatedDate < 2024-03-01T00:00:00Z"


def test_date_conditions_are_replaced_and_other_conditions_kept():
    q = ("SELECT Id, Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' "
         "AND ClosedDate >= 2022-12-01T00:00:00Z AND ClosedDate <= 2023-02-28T23:59:59Z")
    assert RW.rewrite(q, "CreatedDate", START, END) == (
        "SELECT Id, Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND " + WINDOW)


def test_a_query_without_a_window_gets_one_and_loses_its_limit():
    q = "SELECT OwnerId, COUNT(Id) cnt FROM Case WHERE ClosedDate != null GROUP BY OwnerId ORDER BY COUNT(Id) DESC LIMIT 1"
    assert RW.rewrite(q, "CreatedDate", START, END) == (
        f"SELECT OwnerId, COUNT(Id) cnt FROM Case WHERE ClosedDate != null AND {WINDOW} GROUP BY OwnerId ORDER BY COUNT(Id) DESC")
    assert RW.rewrite("SELECT Id, CreatedDate FROM Case LIMIT 5", "CreatedDate", START, END) == (
        f"SELECT Id, CreatedDate FROM Case WHERE {WINDOW}")


def test_date_conditions_of_both_fields_in_one_or_are_one_window():
    q = ("SELECT Id, CreatedDate, ClosedDate, OwnerId FROM Case WHERE (CreatedDate >= 2023-04-01T00:00:00Z AND "
         "CreatedDate <= 2023-06-30T23:59:59Z) OR (ClosedDate >= 2023-04-01T00:00:00Z AND ClosedDate <= 2023-06-30T23:59:59Z)")
    assert RW.rewrite(q, "CreatedDate", START, END) == f"SELECT Id, CreatedDate, ClosedDate, OwnerId FROM Case WHERE {WINDOW}"


def test_relative_and_function_date_conditions_count_as_windows():
    for cond in ("CreatedDate = LAST_N_DAYS:90", "CALENDAR_YEAR(CreatedDate) = 2023", "ClosedDate > 2021-10-01T00:00:00.000Z",
                 "Case__r.CreatedDate < 2023-01-01"):
        assert RW.classify(cond) == "window", cond
    for cond in ("ClosedDate != null", "Field__c = 'Owner Assignment'", "Subject LIKE '%CreatedDate >= 2023-01-01%'",
                 "OrderItemId__c IN (SELECT Id FROM OrderItem WHERE CreatedDate >= 2023-01-01T00:00:00Z)"):
        assert RW.classify(cond) == "other", cond


def test_a_date_condition_sharing_an_or_with_another_condition_cannot_be_rewritten():
    q = "SELECT Id, CreatedDate, ClosedDate FROM Case WHERE CreatedDate < 2023-04-01T00:00:00Z AND (ClosedDate = null OR ClosedDate > 2023-06-30T23:59:59Z)"
    assert RW.rewrite(q, "CreatedDate", START, END) is None


def test_kept_or_conditions_stay_grouped_and_subqueries_are_untouched():
    q = ("SELECT IssueId__c, COUNT(Id) FROM Case WHERE OrderItemId__c IN (SELECT Id FROM OrderItem WHERE Product2Id = '01tWt000006hVQ5IAM') "
         "AND (Status = 'Closed' OR Status = 'New') AND CreatedDate >= 2024-01-15T00:00:00Z GROUP BY IssueId__c")
    assert RW.rewrite(q, "CreatedDate", START, END) == (
        "SELECT IssueId__c, COUNT(Id) FROM Case WHERE OrderItemId__c IN (SELECT Id FROM OrderItem WHERE Product2Id = '01tWt000006hVQ5IAM') "
        f"AND (Status = 'Closed' OR Status = 'New') AND {WINDOW} GROUP BY IssueId__c")


def test_drop_limit_leaves_a_query_without_one_unchanged():
    q = "SELECT Id, CreatedDate\nFROM Case\nWHERE CreatedDate >= 2023-01-01T00:00:00Z"
    assert RW.drop_limit(q) == q
    assert RW.drop_limit("SELECT Id FROM CaseHistory__c ORDER BY CreatedDate DESC LIMIT 50") == (
        "SELECT Id FROM CaseHistory__c ORDER BY CreatedDate DESC")


def test_answers_of_a_tie_follow_the_tie_slot_unless_the_context_settles_ties():
    D = RW.D
    tie = D.Derived("tie", D.NONE, (D.as_id("005Wt000003NDqD"), D.as_id("005Wt000003NDqE")))
    assert RW.answers_of(tie, D.spec_for("handle_time", "lowest")) == {"none": D.NONE, "first": D.as_id("005Wt000003NDqD")}
    assert RW.answers_of(tie, D.spec_for("case_routing", "")) is None
    assert RW.key_claim(["MO"], "state") == ["value", ["mo"]] and RW.key_claim([None], "id") == ["none", []]
