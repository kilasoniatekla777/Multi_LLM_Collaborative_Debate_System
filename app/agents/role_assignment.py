"""
Stage 0.5: deterministic algorithm that turns two Stage 0 self-assessments
into a concrete role assignment for one problem.

With only 2 real providers (OpenAI, Gemini) available, one model must fill
all 3 Solver slots. To avoid a model ever judging its own solution (a known
LLM-as-judge bias), the model that scores itself LOWER on Judge confidence
always ends up solving, and the other judges -- so the Judge for a given
problem never also solved that problem.

The 3 Solver slots get distinct temperature/persona combinations so a single
underlying model produces genuinely different attempts instead of calling
the same prompt three times.
"""

from dataclasses import dataclass

from app.agents.schemas import RoleAssessment

SOLVER_PERSONAS = [
    {
        "slot_id": "Solver_1",
        "temperature": 0.2,
        "persona": (
            "Work carefully and methodically. Show every step explicitly, and "
            "double-check arithmetic, edge cases, and assumptions before "
            "finalizing your answer."
        ),
    },
    {
        "slot_id": "Solver_2",
        "temperature": 0.5,
        "persona": (
            "Solve directly using the most standard, straightforward approach "
            "for this type of problem."
        ),
    },
    {
        "slot_id": "Solver_3",
        "temperature": 0.9,
        "persona": (
            "Before settling on your approach, briefly consider at least one "
            "alternative or unconventional method, then choose and fully solve "
            "with whichever approach you trust most."
        ),
    },
]


@dataclass
class ModelAssessment:
    """One (provider, model)'s Stage 0 self-assessment, bundled for Stage 0.5."""

    provider: str
    model: str
    assessment: RoleAssessment


@dataclass
class SolverSlot:
    slot_id: str
    provider: str
    model: str
    temperature: float
    persona: str


@dataclass
class RoleAssignment:
    judge_provider: str
    judge_model: str
    solver_slots: list[SolverSlot]


def assign_roles(candidates: list[ModelAssessment]) -> RoleAssignment:
    """
    Picks a Judge and fills 3 Solver slots from exactly 2 model candidates.

    Rule: whichever candidate reports higher confidence for "Judge" becomes
    the Judge; the other fills all 3 Solver slots.

    Tie-break, applied in order until broken:
      1. Lower "Solver" confidence -> judges (more suited to judging by
         elimination, since it rated itself as a weaker solver).
      2. Candidate earlier in the input `candidates` list -> judges (the
         caller controls this via ordering, keeping the rule deterministic
         even on a full tie).
    """
    if len(candidates) != 2:
        raise ValueError(f"assign_roles expects exactly 2 candidates, got {len(candidates)}")

    a, b = candidates
    judge_conf_a = a.assessment.confidence_by_role.get("Judge", 0.0)
    judge_conf_b = b.assessment.confidence_by_role.get("Judge", 0.0)

    if judge_conf_a > judge_conf_b:
        judge, solver = a, b
    elif judge_conf_b > judge_conf_a:
        judge, solver = b, a
    else:
        solver_conf_a = a.assessment.confidence_by_role.get("Solver", 0.0)
        solver_conf_b = b.assessment.confidence_by_role.get("Solver", 0.0)
        if solver_conf_a < solver_conf_b:
            judge, solver = a, b
        elif solver_conf_b < solver_conf_a:
            judge, solver = b, a
        else:
            judge, solver = a, b  # fully tied: first candidate in input order judges

    solver_slots = [
        SolverSlot(
            slot_id=p["slot_id"],
            provider=solver.provider,
            model=solver.model,
            temperature=p["temperature"],
            persona=p["persona"],
        )
        for p in SOLVER_PERSONAS
    ]

    return RoleAssignment(
        judge_provider=judge.provider,
        judge_model=judge.model,
        solver_slots=solver_slots,
    )
