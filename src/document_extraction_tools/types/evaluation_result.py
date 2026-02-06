"""Model for evaluation results.

This model defines the output schema used by the evaluation pipeline.
"""

from typing import Any

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Represents a single evaluation result for one document."""

    name: str = Field(..., description="Name of the evaluator or metric.")

    result: Any = Field(..., description="Computed metric value.")

    description: str = Field(..., description="Human-readable description.")

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata associated with the evaluation result.",
    )
