"""Evaluation result model.

This model defines the output schema produced by evaluators.
"""

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Represents a single evaluation result for one document."""

    name: str = Field(..., description="Name of the evaluator or metric.")
    result: float = Field(..., description="Computed metric value.")
    description: str = Field(..., description="Human-readable description.")
