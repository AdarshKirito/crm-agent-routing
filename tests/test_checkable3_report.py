"""Round-3 report: the one-sided Fisher test behind P3, and frozen rule specs that rebuild the same rules."""
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import checkable3_report as R


def test_fisher_one_sided_matches_hand_computed_tables():
    # Fisher's tea tasting: 3 of 4 cups right, P(X >= 3) = (4*4 + 1) / C(8, 4) = 17/70
    assert abs(R.fisher_one_sided(3, 1, 1, 3) - 17 / 70) < 1e-12
    assert R.fisher_one_sided(0, 5, 0, 5) == 1.0
    assert abs(R.fisher_one_sided(2, 0, 0, 2) - comb(2, 2) * comb(2, 0) / comb(4, 2)) < 1e-12


def test_frozen_rule_specs_rebuild_the_same_rules():
    gate = R.R3.Gate([], {})
    for runs_used, kind in ((3, "pinned"), (2, "pinned"), (1, "pinned"), (3, "none")):
        rule = R.R3.make_rule(runs_used, kind, gate if kind != "none" else None, (), frozenset({"handle_time"}))
        spec = R.spec_of(rule)
        again = R.rule_from(spec, gate)
        assert again.__name__ == rule.__name__ and (again.runs_used, again.gate_kind) == (runs_used, kind)
    assert R.rule_from({"rule": None}, gate) is R.WITHHOLD_ALL
