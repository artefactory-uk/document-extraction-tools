"""Configuration for Evaluator components."""

from typing import ClassVar

from pydantic import BaseModel, Field


class BaseEvaluatorConfig(BaseModel):
    """Base config for Evaluators.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "evaluator.yaml"
    evaluator_name: str = Field(..., description="Evaluator identifier.")
