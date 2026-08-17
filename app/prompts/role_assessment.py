"""Prompt template for Stage 0: role self-assessment."""

SYSTEM_PROMPT = (
    "You are one of several LLMs participating in a multi-agent debate system. "
    "For each problem, three LLMs act as independent Solvers who each produce a "
    "solution, review each other's work, and refine their answers based on that "
    "feedback. A fourth LLM acts as Judge, reviewing all solutions and picking "
    "the best final answer. You are being asked to self-assess which role you "
    "would perform best on the specific problem below, before any role has been "
    "assigned."
)

RESPONSE_FORMAT_INSTRUCTIONS = """
Respond with ONLY a single JSON object, no markdown code fences, no extra text, matching this shape:

{
  "role_preferences": ["Solver", "Judge"],
  "confidence_by_role": {"Solver": 0.0, "Judge": 0.0},
  "reasoning": "one or two sentences on why"
}

- "role_preferences" must be ordered from most to least preferred.
- "confidence_by_role" must include both "Solver" and "Judge" with values between 0 and 1.
"""


def build_role_assessment_prompt(question: str) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the Stage 0 self-assessment call."""
    user_prompt = (
        f"Problem:\n{question}\n\n"
        "Which role -- Solver or Judge -- do you think you would perform best "
        "in for this specific problem? Consider the problem's category and what "
        f"kind of reasoning it demands.\n{RESPONSE_FORMAT_INSTRUCTIONS}"
    )
    return SYSTEM_PROMPT, user_prompt
