"""Pydantic schemas for structured LLM outputs, one per debate stage."""

from typing import Literal

from pydantic import BaseModel, field_validator

Role = Literal["Solver", "Judge"]


class RoleAssessment(BaseModel):
    """Stage 0 output: how one LLM rates itself for each role on a specific question."""

    role_preferences: list[Role]
    confidence_by_role: dict[Role, float]
    reasoning: str

    @field_validator("confidence_by_role")
    @classmethod
    def scores_in_range(cls, v: dict[Role, float]) -> dict[Role, float]:
        for role, score in v.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"confidence for {role} must be between 0 and 1, got {score}")
        return v

    @field_validator("role_preferences")
    @classmethod
    def preferences_nonempty(cls, v: list[Role]) -> list[Role]:
        if not v:
            raise ValueError("role_preferences must not be empty")
        return v


class SolverSolution(BaseModel):
    """Stage 1 output: one Solver instance's independent attempt at a problem."""

    reasoning: str
    final_answer: str
    confidence: float

    @field_validator("confidence")
    @classmethod
    def confidence_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"confidence must be between 0 and 1, got {v}")
        return v
