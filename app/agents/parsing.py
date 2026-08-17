"""Shared JSON parsing/validation for structured LLM stage outputs."""

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def extract_json(raw: str) -> dict:
    """Strip markdown code fences some models add despite instructions not to."""
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    return json.loads(text)


def parse_structured_response(raw: str, schema: type[T], context: str) -> T:
    """
    Parses and validates a raw LLM reply against `schema`.

    context: identifies the caller (e.g. "openai/gpt-4o-mini" or a solver
    slot id) so a parsing failure points at which call produced it.
    """
    try:
        data = extract_json(raw)
        return schema(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(
            f"{context} returned an unparsable response: {e}\nRaw response: {raw!r}"
        ) from e
