"""Configuration for example evaluators."""

from typing import ClassVar

from document_extraction_tools.config.evaluator_config import BaseEvaluatorConfig


class AccuracyEvaluatorConfig(BaseEvaluatorConfig):
    """Configuration for the accuracy evaluator."""

    filename: ClassVar[str] = "accuracy_evaluator.yaml"


class F1EvaluatorConfig(BaseEvaluatorConfig):
    """Configuration for the F1 evaluator."""

    filename: ClassVar[str] = "f1_evaluator.yaml"
