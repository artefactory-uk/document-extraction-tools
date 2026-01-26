"""Configuration for example evaluators."""

from pydantic import Field

from document_extraction_tools.config.base_evaluator_config import BaseEvaluatorConfig


class AccuracyEvaluatorConfig(BaseEvaluatorConfig):
    """Configuration for the accuracy evaluator."""

    use_llm_judge: bool = Field(
        default=False,
        description="Whether to use an LLM as a judge for value equality.",
    )
    llm_judge_model: str | None = Field(
        default=None,
        description="Model name to use for LLM-as-a-judge comparisons.",
    )
    llm_judge_prompt: str | None = Field(
        default=None,
        description="Prompt template for LLM-as-a-judge comparisons.",
    )


class F1EvaluatorConfig(BaseEvaluatorConfig):
    """Configuration for the F1 evaluator."""

    use_llm_judge: bool = Field(
        default=False,
        description="Whether to use an LLM as a judge for value equality.",
    )
    llm_judge_model: str | None = Field(
        default=None,
        description="Model name to use for LLM-as-a-judge comparisons.",
    )
    llm_judge_prompt: str | None = Field(
        default=None,
        description="Prompt template for LLM-as-a-judge comparisons.",
    )
