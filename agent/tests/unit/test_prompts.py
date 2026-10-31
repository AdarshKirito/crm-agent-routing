"""The hints ablation (CRMROUTE_TASK_HINTS=0) removes only the per-task-type hint lines."""

from types import SimpleNamespace

from app import prompts
from app import state_keys as K
from app.task_specs import SPECS

BUSINESS = {name: spec for name, spec in SPECS.items() if spec.answer != "refusal"}


def solver_prompt(task_type: str) -> str:
    state = {K.ORG: "b2b", K.AUDIENCE: "employee", K.ROUTE: {"task_type": task_type, "confidence": 0.9}}
    return prompts.solver_instruction(SimpleNamespace(state=state))


def test_every_business_type_gets_its_hints_by_default():
    for task_type, spec in BUSINESS.items():
        text = solver_prompt(task_type)
        assert spec.hints and all(hint in text for hint in spec.hints), task_type


def test_hints_off_keeps_goal_and_answer_form(monkeypatch):
    monkeypatch.setattr(prompts, "TASK_HINTS", False)
    for task_type, spec in BUSINESS.items():
        text = solver_prompt(task_type)
        assert not any(hint in text for hint in spec.hints), task_type
        assert spec.goal in text and prompts.ANSWER_FORMS[spec.answer] in text, task_type
