import math

import pytest

from checkable import Question, Run, agreement_rule, certify, evaluate, upper_bound


def test_clopper_pearson_matches_the_closed_form_with_no_errors():
    for n in (10, 30, 144):
        assert upper_bound(0, n, 0.05) == pytest.approx(1 - 0.05 ** (1 / n), abs=1e-9)
    assert upper_bound(3, 3, 0.05) == 1.0 and upper_bound(0, 0, 0.05) == 1.0


def test_round_three_figure_is_reproduced():
    # crmroute round 3, test half: 7 wrong of 144 released, exact one-sided 95% bound 8.9%
    assert round(100 * upper_bound(7, 144, 0.05), 1) == 8.9


def q(i, answers, correct, kind="t", flags=()):
    return Question(i, kind, [Run(a, correct, frozenset(flags)) for a in answers])


def test_agreement_rule_withholds_disagreement_flags_kinds_and_failed_gates():
    rule = agreement_rule(refuse_flags=["budget"], withhold_kinds=["free_text"], gated_kinds=["region"])
    assert rule(q(1, "AAA", True))
    assert not rule(q(2, "AAB", True))
    assert not rule(q(3, "AAA", True, flags=["budget"]))
    assert not rule(q(4, "AAA", True, kind="free_text"))
    gated = q(5, "AAA", True, kind="region")
    assert not rule(gated)
    gated.gate = "pass"
    assert rule(gated)


def test_certify_stops_at_the_first_failure_and_picks_the_widest_certified():
    # 60 easy questions all right; 40 harder ones, 12 wrong
    easy = [q(i, "AAA", True, kind="easy") for i in range(60)]
    hard = [q(100 + i, "BBB", i >= 12, kind="hard") for i in range(40)]
    strict = agreement_rule(withhold_kinds=["hard"])
    loose = agreement_rule()
    cert = certify(easy + hard, [strict, loose], alpha=0.10, delta=0.10)
    assert [o.certified for o in cert.tested] == [True, False]
    assert cert.rule is strict
    assert cert.tested[0].p_value == pytest.approx(0.9 ** 60)
    assert evaluate(easy + hard, loose).wrong == 12


def test_certify_with_nothing_certified_withholds_everything():
    cert = certify([q(i, "AAA", False) for i in range(5)], [agreement_rule()])
    assert cert.rule is None and "none" in cert.table()
    assert math.isclose(cert.tested[0].p_value, 1.0)
