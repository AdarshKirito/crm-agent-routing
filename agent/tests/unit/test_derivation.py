import random
from datetime import datetime, timedelta, timezone

from app import derivation as D
from app.receipt_check import ID_RE, parse_claim

A, B, C = "005Wt000003NDqDIAW", "005Wt000003NDqEIAW", "005Wt000003NDqFIAW"
ISSUE1, ISSUE2 = "a03Wt00000JqnHwIAJ", "a03Wt00000JqtOtIAJ"
PRODUCT = "01tWt000006hV6jIAE"
B2B_POLICY = "this filter applies to both the first agent that the case was first assigned to and the agent ..."
ORIGINAL_POLICY = "this filter applies to the first agent that the case was first assigned to. This means ..."


def ts(day: int, hour: int = 0) -> str:
    return (datetime(2023, 1, 1, tzinfo=timezone.utc) + timedelta(days=day, hours=hour)).strftime("%Y-%m-%dT%H:%M:%S.000+0000")


def cid(n: int) -> str:
    return f"500Wt0000{n:06d}AAA"


def case(n: int, owner=None, state=None, opened=0, hours=None, issue=None, status=None, product=None) -> dict:
    row = {"Id": cid(n), "CreatedDate": ts(opened)}
    if hours is not None:
        row["ClosedDate"] = ts(opened, hours)
    if owner:
        row["OwnerId"] = owner
    if state:
        row["Account.ShippingState"] = state
    if issue:
        row["IssueId__c"] = issue
    if status:
        row["Status"] = status
    if product:
        row["OrderItemId__r.Product2Id"] = product
    return row


def assignment(case_n: int, new, old=None, day=0) -> dict:
    return {"CaseId__c": cid(case_n), "Field__c": "Owner Assignment",
            "OldValue__c": old, "NewValue__c": new, "CreatedDate": ts(day)}


BRI = "SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null"
HT = "SELECT Id, CreatedDate, ClosedDate, OwnerId FROM Case WHERE CreatedDate >= 2023-01-01T00:00:00Z"
HIST = "SELECT CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE Field__c = 'Owner Assignment'"
MTA = f"SELECT Id, CreatedDate FROM Case WHERE OrderItemId__r.Product2Id = '{PRODUCT}'"
TII = f"SELECT IssueId__c, COUNT(Id) FROM Case WHERE OrderItemId__r.Product2Id = '{PRODUCT}' GROUP BY IssueId__c ORDER BY COUNT(Id) DESC LIMIT 1"
CR = "SELECT OwnerId, COUNT(Id) cnt FROM Case WHERE IssueId__c = 'a03Wt00000JqvvOIAR' AND Status = 'Closed' GROUP BY OwnerId"


def spec(task_type, question="", context=B2B_POLICY):
    return D.spec_for(task_type, question, context)


def test_id_pattern_matches_receipt_check():
    assert D.ID_RE.pattern == ID_RE.pattern


def test_answers_compare_with_claims():
    assert D.as_id(A[:15]) == parse_claim(A, "id").key()
    assert D.as_value("TX") == parse_claim("TX", "state").key()
    assert D.as_month("2023-05") == parse_claim("May", "month").key()
    assert D.NONE == parse_claim("None", "id").key()


def test_parse_query_names_columns_as_salesforce_does():
    q = D.parse_query("SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE Subject LIKE '%FROM x%' "
                      "AND OrderItemId__c IN (SELECT Id FROM OrderItem) GROUP BY CALENDAR_MONTH(CreatedDate)")
    assert (q.obj, q.grouped) == ("case", True)
    assert [k for _, k in q.columns] == ["expr0", "expr1"]
    q = D.parse_query("SELECT OwnerId, COUNT(Id) cnt FROM Case GROUP BY OwnerId")
    assert q.columns == (("OwnerId", "OwnerId"), ("COUNT(Id)", "cnt")) and q.aggregate("COUNT") == "cnt"
    q = D.parse_query("select Id, Account.ShippingState from case")
    assert (q.obj, q.grouped, q.column("shippingstate")) == ("case", False, "Account.ShippingState")
    assert D.parse_query("FIND {x} IN ALL FIELDS RETURNING Case(Id)") is None


def test_spec_reads_direction_filter_scope_and_product():
    s = spec("handle_time", "Which agent had the lowest average handle time for those processing more than one case?")
    assert (s.direction, s.min_cases, s.scope) == ("min", (1, False), "both")
    s = spec("transfer_count", "the highest number of transfers among those handling at least one case", ORIGINAL_POLICY)
    assert (s.direction, s.min_cases, s.scope) == ("max", (1, True), "first")
    assert spec("transfer_count", "who managed more than zero cases, with the fewest transfers").min_cases == (0, False)
    assert spec("handle_time", "Which agent handled cases?").direction is None
    assert spec("monthly_trend_analysis", f"The associated product Id is {PRODUCT}. Return only").product == PRODUCT[:15]
    assert spec("case_routing").tie_rule and not spec("handle_time", "lowest").tie_rule


def test_best_region_is_the_state_with_the_quickest_mean_closure():
    rows = [case(1, state="TX", hours=2), case(2, state="TX", hours=4), case(3, state="CA", hours=1),
            case(4, state="CA", hours=7), case(5, state="MO")]  # mean TX 3 h, CA 4 h; MO is open
    d = D.derive(spec("best_region_identification", "quickest case closures"), BRI, rows)
    assert (d.status, d.answer) == ("ok", ("value", ("tx",)))
    assert D.derive(spec("best_region_identification"), BRI, []).answer == D.NONE
    tie = D.derive(spec("best_region_identification"), BRI, [case(1, state="TX", hours=2), case(2, state="CA", hours=2)])
    assert tie.status == "tie" and tie.answers() == {D.NONE, ("value", ("ca",))}
    assert D.derive(spec("best_region_identification"), "SELECT Id, CreatedDate FROM Case", rows) is None


def test_handle_time_leaves_transferred_cases_out_and_counts_managed_cases_by_policy():
    q = "In the past four months, which agent had the lowest average handle time for those processing more than one case?"
    rows = [case(1, owner=A, hours=1), case(2, owner=A, hours=9), case(3, owner=B, hours=2), case(4, owner=B, hours=4)]
    assert D.derive(spec("handle_time", q), HT, rows).answer == D.as_id(B[:15])  # A 5 h, B 3 h
    history = D.history_from([assignment(3, C), assignment(3, B, old=C, day=1), assignment(4, B)], D.parse_query(HIST))
    assert history == {cid(3)[:15]: [C[:15], B[:15]], cid(4)[:15]: [B[:15]]}
    # case 3 was transferred: B's handle time is 4 h now, still under A's 5 h; B managed 2 cases either way
    assert D.derive(spec("handle_time", q), HT, rows, history).answer == D.as_id(B[:15])
    # counted by the first agent only (the original org's policy), B managed one case: filtered out
    assert D.derive(spec("handle_time", q, ORIGINAL_POLICY), HT, rows, history).answer == D.as_id(A[:15])


def test_transfer_count_counts_transfers_from_each_agent_among_managing_agents():
    q = D.parse_query(HIST)
    rows = [assignment(1, A), assignment(1, B, old=A, day=1), assignment(2, A), assignment(2, C, old=A, day=2),
            assignment(3, B), assignment(3, C, old=B, day=3), assignment(4, C)]
    assert D.derive(spec("transfer_count", "the highest number of transfers"), q.text, rows).answer == D.as_id(A[:15])
    low = D.derive(spec("transfer_count", "the lowest transfer counts among those managing more than one case"), q.text, rows)
    assert low.answer == D.as_id(C[:15])  # C has 0 transfers and manages 3 cases; A 2, B 1
    first = D.derive(spec("transfer_count", "the lowest transfer counts among those managing more than one case",
                          ORIGINAL_POLICY), q.text, rows)
    assert first.answer == D.as_id(A[:15])  # counted by first assignment, only A (2 cases) manages more than one
    grouped = "SELECT OldValue__c, COUNT(Id) cnt FROM CaseHistory__c WHERE OldValue__c != null GROUP BY OldValue__c"
    assert D.derive(spec("transfer_count", "lowest"), grouped,
                    [{"OldValue__c": A, "cnt": 2}, {"OldValue__c": B, "cnt": 1}]).answer == D.as_id(B[:15])


def test_monthly_trend_counts_cases_per_month_of_the_product():
    s = spec("monthly_trend_analysis", f"The associated product Id is {PRODUCT}.")
    rows = [case(1, opened=0), case(2, opened=40), case(3, opened=41), case(4, opened=70)]  # Jan, Feb, Feb, Mar
    assert D.derive(s, MTA, rows).answer == ("value", ("february",))
    unfiltered = "SELECT Id, CreatedDate, OrderItemId__r.Product2Id FROM Case WHERE CreatedDate >= 2023-01-01T00:00:00Z"
    other = "01tWt000006hV9xIAE"
    rows = [case(1, opened=0, product=PRODUCT), case(2, opened=40, product=other), case(3, opened=41, product=other)]
    assert D.derive(s, unfiltered, rows).answer == ("value", ("january",))  # rows are filtered to the product
    assert D.derive(s, "SELECT Id, CreatedDate FROM Case", rows) is None  # not limited to the product
    grouped = (f"SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE OrderItemId__r.Product2Id = '{PRODUCT}' "
               "GROUP BY CALENDAR_MONTH(CreatedDate)")
    assert D.derive(s, grouped, [{"expr0": 3, "expr1": 2}, {"expr0": 11, "expr1": 5}]).answer == ("value", ("november",))


def test_monthly_trend_names_one_month_when_its_best_counts_fall_in_two_years():
    s = spec("monthly_trend_analysis", f"The associated product Id is {PRODUCT}.")
    jan23, jan24, feb23 = [case(1, opened=0), case(2, opened=1)], [case(3, opened=365), case(4, opened=366)], [case(5, opened=40)]
    assert D.derive(s, MTA, jan23 + jan24 + feb23).answer == ("value", ("january",))
    assert D.derive(s, MTA, jan23[:1] + jan24[:1] + feb23).status == "tie"  # one case each: January or February


def test_top_issue_and_case_routing_count_per_group():
    s = spec("top_issue_identification", f"The associated product Id is {PRODUCT}.")
    assert D.derive(s, TII, [{"IssueId__c": ISSUE1, "expr0": 2}, {"IssueId__c": ISSUE2, "expr0": 3}]).answer == D.as_id(ISSUE2[:15])
    assert D.derive(s, "SELECT IssueId__c, COUNT(Id) FROM Case GROUP BY IssueId__c", []) is None  # any product
    assert D.derive(spec("case_routing"), CR, [{"OwnerId": A, "cnt": 4}, {"OwnerId": B, "cnt": 6}]).answer == D.as_id(B[:15])
    raw = "SELECT Id, OwnerId, Status FROM Case WHERE IssueId__c = 'a03Wt00000JqvvOIAR'"
    rows = [case(1, owner=A, status="Closed"), case(2, owner=B, status="New"), case(3, owner=B, status="New")]
    assert D.derive(spec("case_routing"), raw, rows).answer == D.as_id(A[:15])  # only closed cases count


# ---- metamorphic relations: what must hold however the rows look ---------------------------------


def random_rows(rng, n):
    owners, issues = (A, B, C), (ISSUE1, ISSUE2)
    return [case(i, owner=rng.choice(owners), state=rng.choice(("TX", "CA", "MO")), opened=rng.randrange(0, 300),
                 hours=rng.randrange(1, 200), issue=rng.choice(issues), status="Closed") for i in range(n)]


COUNTED = [  # (spec, query) of the count-based derivations, over the same case rows
    (spec("monthly_trend_analysis", f"The associated product Id is {PRODUCT}."), MTA),
    (spec("top_issue_identification", f"The associated product Id is {PRODUCT}."),
     f"SELECT Id, IssueId__c FROM Case WHERE OrderItemId__r.Product2Id = '{PRODUCT}'"),
    (spec("case_routing"), "SELECT Id, OwnerId, Status FROM Case"),
]


def test_a_wider_window_cannot_lower_a_count():
    rng = random.Random(7)
    for _ in range(50):
        rows = random_rows(rng, rng.randrange(1, 40))
        cut = rng.randrange(0, 300)
        narrow = [r for r in rows if r["CreatedDate"] < ts(cut)]
        for s, q in COUNTED:
            wide, small = dict(D.derive(s, q, rows).scores), dict(D.derive(s, q, narrow).scores)
            assert all(wide[g] >= n for g, n in small.items())


def test_enough_injected_records_make_the_runner_up_the_answer():
    rng = random.Random(11)
    for _ in range(50):
        rows = random_rows(rng, rng.randrange(2, 40))
        s, q = COUNTED[2]
        d = D.derive(s, q, rows)
        if len(d.scores) < 2:
            continue
        (best, n_best), (second, n_second) = d.scores[0], d.scores[1]
        extra = [case(1000 + i, owner=second, status="Closed") for i in range(int(n_best - n_second) + 1)]
        assert D.derive(s, q, rows + extra).answer == D.as_id(second)


def test_row_order_and_duplicate_rows_do_not_change_mean_answers():
    rng = random.Random(5)
    q = "In the past year, which agent had the highest average handle time?"
    for _ in range(50):
        rows = random_rows(rng, rng.randrange(1, 30))
        shuffled = rng.sample(rows, len(rows))
        for s, text in ((spec("best_region_identification"), BRI), (spec("handle_time", q), HT)):
            d = D.derive(s, text, rows)
            assert D.derive(s, text, shuffled).answers() == d.answers()
            assert D.derive(s, text, rows + rows).answers() == d.answers()
