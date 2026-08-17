"""
Smoke test for Stage 1 solving.

Makes a real API call (no mocking), so it's skipped if OPENAI_API_KEY isn't
set -- same pattern as the other stage tests.
"""

import json
import os

import pytest

from app.agents.role_assignment import SOLVER_PERSONAS, SolverSlot
from app.agents.solver import solve

with open("data/debate_problems_25.json") as f:
    _QUESTION = json.load(f)[2]["question"]  # prob_03: dice sum is prime -- cheap to check


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)
def test_solve_openai_returns_valid_schema():
    slot = SolverSlot(
        slot_id="Solver_1",
        provider="openai",
        model="gpt-4o-mini",
        temperature=SOLVER_PERSONAS[0]["temperature"],
        persona=SOLVER_PERSONAS[0]["persona"],
    )
    result = solve(slot, _QUESTION)
    assert isinstance(result.final_answer, str) and len(result.final_answer) > 0
    assert 0.0 <= result.confidence <= 1.0
