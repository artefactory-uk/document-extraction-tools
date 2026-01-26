"""Configuration for Evaluator components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseEvaluatorConfig(BaseModel):
    """Base config for Evaluators.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "evaluator.yaml"
