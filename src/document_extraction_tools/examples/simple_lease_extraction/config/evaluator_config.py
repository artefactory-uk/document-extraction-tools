"""Configuration for example evaluators."""

from typing import ClassVar

from pydantic import Field

from document_extraction_tools.config.base_evaluator_config import BaseEvaluatorConfig


class AccuracyEvaluatorConfig(BaseEvaluatorConfig):
    """Configuration for the accuracy evaluator."""

    filename: ClassVar[str] = "accuracy_evaluator.yaml"
    use_llm_judge: bool = Field(
        default=False,
        description="Whether to use an LLM as a judge for value equality.",
    )


class F1EvaluatorConfig(BaseEvaluatorConfig):
    """Configuration for the F1 evaluator."""

    filename: ClassVar[str] = "f1_evaluator.yaml"
    use_llm_judge: bool = Field(
        default=False,
        description="Whether to use an LLM as a judge for value equality.",
    )
