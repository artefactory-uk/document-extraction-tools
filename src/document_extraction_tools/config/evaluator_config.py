"""Configuration for Evaluator components."""

from pydantic import BaseModel, Field


class BaseEvaluatorConfig(BaseModel):
    """Base config for Evaluators.

    Implementations should subclass this to add specific parameters.
    """

    evaluator_name: str = Field(..., description="Evaluator identifier.")
