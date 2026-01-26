"""Configuration for the Gemini with images extractor."""

from pydantic import Field

from document_extraction_tools.config.base_extractor_config import BaseExtractorConfig


class GeminiImageExtractorConfig(BaseExtractorConfig):
    """Configuration for the Gemini with images extractor."""

    model_name: str = Field(
        default="gemini-3-flash-preview",
        description="Gemini model to use for extraction.",
    )
    mlflow_prompt_name: str = Field(
        default=...,
        description="MLflow prompt name to use for prompt retrieval.",
    )
    mlflow_prompt_version: int = Field(
        default=...,
        description="MLflow prompt version to use for prompt retrieval.",
    )
