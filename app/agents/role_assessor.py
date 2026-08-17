"""Stage 0: each LLM self-assesses which role it would perform best."""

from app.agents.parsing import parse_structured_response
from app.agents.schemas import RoleAssessment
from app.llm.client import call_llm
from app.prompts.role_assessment import build_role_assessment_prompt


def assess_role(provider: str, model: str, question: str) -> RoleAssessment:
    """Calls one LLM to self-assess Solver vs. Judge fit for a given question."""
    system_prompt, user_prompt = build_role_assessment_prompt(question)
    raw = call_llm(provider, model, system_prompt, user_prompt)
    return parse_structured_response(raw, RoleAssessment, context=f"{provider}/{model}")
