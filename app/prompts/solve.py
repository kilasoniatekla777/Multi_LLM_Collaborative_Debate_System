"""Prompt template for Stage 1: independent solution generation."""

BASE_SYSTEM_PROMPT = (
    "You are one of three independent Solvers in a multi-agent debate system. "
    "You will be given a problem and must produce your own complete solution "
    "with clear step-by-step reasoning. You cannot see what the other Solvers "
    "are doing -- work entirely on your own."
)

RESPONSE_FORMAT_INSTRUCTIONS = """
Respond with ONLY a single JSON object, no markdown code fences, no extra text, matching this shape:

{
  "reasoning": "your full step-by-step reasoning",
  "final_answer": "your final answer, stated concisely and precisely",
  "confidence": 0.0
}

- "final_answer" must be precise enough to be checked against a ground-truth answer (a number, an exact phrase, an expression -- not a vague description).
- "confidence" is your own confidence in "final_answer", between 0 and 1.
"""


def build_solve_prompt(question: str, persona: str) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for a Stage 1 solve call.

    persona: the SolverSlot's persona text (from role_assignment.py),
    merged into the base system prompt so each of the 3 slots reasons
    differently even when they share an underlying model.
    """
    system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{persona}"
    user_prompt = f"Problem:\n{question}\n{RESPONSE_FORMAT_INSTRUCTIONS}"
    return system_prompt, user_prompt
