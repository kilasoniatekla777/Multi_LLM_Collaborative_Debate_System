"""
Basic smoke tests for app/llm/client.py.

These make real API calls (no mocking) so they're skipped automatically
if the relevant API key isn't set in your environment/.env file. That
keeps `pytest` runnable for anyone who clones the repo without keys,
while still giving you a real signal when you DO have keys configured.
"""

import os
import pytest
from app.llm.client import call_openai, call_gemini


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)
def test_call_openai_returns_text():
    result = call_openai(
        model="gpt-4o-mini",
        system_prompt="You are a helpful assistant.",
        user_prompt="Reply with exactly the word: pong",
    )
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY not set",
)
def test_call_gemini_returns_text():
    # This test will fail with NotImplementedError until you implement
    # call_gemini in app/llm/client.py -- that's expected and intentional.
    result = call_gemini(
        model="gemini-1.5-flash",
        system_prompt="You are a helpful assistant.",
        user_prompt="Reply with exactly the word: pong",
    )
    assert isinstance(result, str)
    assert len(result) > 0
