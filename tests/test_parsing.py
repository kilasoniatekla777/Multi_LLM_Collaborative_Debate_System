"""
Unit tests for the shared JSON parsing/validation helper. Pure logic, no
LLM calls, no API keys needed -- these always run.
"""

import pytest
from pydantic import BaseModel

from app.agents.parsing import extract_json, parse_structured_response


class _Dummy(BaseModel):
    value: int


def test_extract_json_plain():
    assert extract_json('{"value": 1}') == {"value": 1}


def test_extract_json_markdown_fenced():
    raw = '```json\n{"value": 2}\n```'
    assert extract_json(raw) == {"value": 2}


def test_parse_structured_response_valid():
    result = parse_structured_response('{"value": 3}', _Dummy, context="test")
    assert result.value == 3


def test_parse_structured_response_invalid_json_raises_with_context():
    with pytest.raises(ValueError, match="test"):
        parse_structured_response("not json", _Dummy, context="test")


def test_parse_structured_response_schema_violation_raises():
    with pytest.raises(ValueError):
        parse_structured_response('{"wrong_field": 1}', _Dummy, context="test")
