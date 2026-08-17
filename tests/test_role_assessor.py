"""
Smoke test for Stage 0 role self-assessment.

Makes a real API call (no mocking), so it's skipped if OPENAI_API_KEY isn't
set -- same pattern as tests/test_llm_client.py.
"""

import json
import os

import pytest

from app.agents.role_assessor import assess_role

with open("data/debate_problems_25.json") as f:
    _QUESTION = json.load(f)[0]["question"]


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)
def test_assess_role_openai_returns_valid_schema():
    result = assess_role(provider="openai", model="gpt-4o-mini", question=_QUESTION)
    assert set(result.confidence_by_role) >= {"Solver", "Judge"}
    assert len(result.role_preferences) > 0
