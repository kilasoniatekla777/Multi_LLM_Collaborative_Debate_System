"""Stage 1: each Solver instance independently produces a solution."""

from app.agents.parsing import parse_structured_response
from app.agents.role_assignment import SolverSlot
from app.agents.schemas import SolverSolution
from app.llm.client import call_llm
from app.prompts.solve import build_solve_prompt


def solve(slot: SolverSlot, question: str) -> SolverSolution:
    """Runs one Solver slot against a problem and returns its solution."""
    system_prompt, user_prompt = build_solve_prompt(question, slot.persona)
    raw = call_llm(
        slot.provider, slot.model, system_prompt, user_prompt, temperature=slot.temperature
    )
    return parse_structured_response(
        raw, SolverSolution, context=f"{slot.slot_id} ({slot.provider}/{slot.model})"
    )
