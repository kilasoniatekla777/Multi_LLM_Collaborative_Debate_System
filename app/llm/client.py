"""
Thin, transparent wrappers around each provider's native SDK.

Why not use a unifying library like litellm here?
Because the point of this module, for now, is to SEE what each provider's
API actually looks like -- their request shape, their response shape, and
how each one handles asking for structured JSON output. That knowledge is
worth more right now than the convenience of a single call signature.

Every agent in app/agents/ will eventually call call_llm() below and never
touch the provider-specific functions directly. That's the seam where we
could swap in litellm later without changing any agent code, if it turns
out to be worth it.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

load_dotenv()  # reads .env into environment variables, once, at import time

_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))


def call_openai(
    model: str, system_prompt: str, user_prompt: str, temperature: float | None = None
) -> str:
    """
    Call an OpenAI chat model and return the plain text response.

    model: e.g. "gpt-4o", "gpt-4o-mini"
    system_prompt: sets the agent's role/instructions
    user_prompt: the actual question/content for this turn
    temperature: sampling temperature; omitted (provider default) if None

    Returns the raw text content of the model's reply.
    """
    kwargs = {} if temperature is None else {"temperature": temperature}
    response = _openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return response.choices[0].message.content


def call_gemini(
    model: str, system_prompt: str, user_prompt: str, temperature: float | None = None
) -> str:
    """
    Call a Google Gemini model and return the plain text response.

    temperature: sampling temperature; omitted (provider default) if None
    """
    model_obj = genai.GenerativeModel(model_name=model, system_instruction=system_prompt)
    generation_config = None if temperature is None else {"temperature": temperature}
    response = model_obj.generate_content(user_prompt, generation_config=generation_config)
    return response.text


def call_llm(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float | None = None,
) -> str:
    """
    Single entry point every agent should use, instead of calling
    call_openai/call_gemini directly. This is the seam that keeps agent
    code provider-agnostic.

    provider: "openai" or "google"
    """
    if provider == "openai":
        return call_openai(model, system_prompt, user_prompt, temperature=temperature)
    elif provider == "google":
        return call_gemini(model, system_prompt, user_prompt, temperature=temperature)
    else:
        raise ValueError(f"Unknown provider: {provider}")
