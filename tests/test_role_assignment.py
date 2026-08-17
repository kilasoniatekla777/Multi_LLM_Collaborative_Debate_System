"""
Unit tests for Stage 0.5 role assignment. Pure logic, no LLM calls, no API
keys needed -- these always run.
"""

import pytest

from app.agents.role_assignment import ModelAssessment, assign_roles
from app.agents.schemas import RoleAssessment


def _assessment(judge_conf: float, solver_conf: float) -> RoleAssessment:
    return RoleAssessment(
        role_preferences=["Judge", "Solver"] if judge_conf >= solver_conf else ["Solver", "Judge"],
        confidence_by_role={"Judge": judge_conf, "Solver": solver_conf},
        reasoning="test",
    )


def test_higher_judge_confidence_wins_judge_role():
    gpt = ModelAssessment("openai", "gpt-4o-mini", _assessment(judge_conf=0.9, solver_conf=0.5))
    gemini = ModelAssessment("google", "gemini-1.5-flash", _assessment(judge_conf=0.3, solver_conf=0.8))

    result = assign_roles([gpt, gemini])

    assert (result.judge_provider, result.judge_model) == ("openai", "gpt-4o-mini")
    assert len(result.solver_slots) == 3
    assert all(s.provider == "google" and s.model == "gemini-1.5-flash" for s in result.solver_slots)


def test_order_of_candidates_does_not_change_outcome():
    gpt = ModelAssessment("openai", "gpt-4o-mini", _assessment(judge_conf=0.9, solver_conf=0.5))
    gemini = ModelAssessment("google", "gemini-1.5-flash", _assessment(judge_conf=0.3, solver_conf=0.8))

    result = assign_roles([gemini, gpt])

    assert (result.judge_provider, result.judge_model) == ("openai", "gpt-4o-mini")


def test_tie_on_judge_confidence_breaks_on_lower_solver_confidence():
    gpt = ModelAssessment("openai", "gpt-4o-mini", _assessment(judge_conf=0.6, solver_conf=0.4))
    gemini = ModelAssessment("google", "gemini-1.5-flash", _assessment(judge_conf=0.6, solver_conf=0.7))

    result = assign_roles([gpt, gemini])

    # gpt has lower solver confidence -> judges by elimination
    assert (result.judge_provider, result.judge_model) == ("openai", "gpt-4o-mini")


def test_full_tie_falls_back_to_input_order():
    gpt = ModelAssessment("openai", "gpt-4o-mini", _assessment(judge_conf=0.5, solver_conf=0.5))
    gemini = ModelAssessment("google", "gemini-1.5-flash", _assessment(judge_conf=0.5, solver_conf=0.5))

    result = assign_roles([gpt, gemini])
    assert (result.judge_provider, result.judge_model) == ("openai", "gpt-4o-mini")

    result2 = assign_roles([gemini, gpt])
    assert (result2.judge_provider, result2.judge_model) == ("google", "gemini-1.5-flash")


def test_solver_slots_have_distinct_temperatures_and_personas():
    gpt = ModelAssessment("openai", "gpt-4o-mini", _assessment(judge_conf=0.9, solver_conf=0.5))
    gemini = ModelAssessment("google", "gemini-1.5-flash", _assessment(judge_conf=0.3, solver_conf=0.8))

    result = assign_roles([gpt, gemini])

    slot_ids = [s.slot_id for s in result.solver_slots]
    temps = [s.temperature for s in result.solver_slots]
    personas = [s.persona for s in result.solver_slots]

    assert slot_ids == ["Solver_1", "Solver_2", "Solver_3"]
    assert len(set(temps)) == 3
    assert len(set(personas)) == 3


def test_wrong_number_of_candidates_raises():
    gpt = ModelAssessment("openai", "gpt-4o-mini", _assessment(judge_conf=0.9, solver_conf=0.5))
    with pytest.raises(ValueError):
        assign_roles([gpt])
