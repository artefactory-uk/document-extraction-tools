"""Configuration for the example extractor."""

from pydantic import Field

from document_extraction_tools.config.extractor_config import BaseExtractorConfig


class ExtractorConfig(BaseExtractorConfig):
    """Configuration for the Gemini extractor."""

    model_name: str = Field(
        default="gemini-3-flash-preview",
        description="Gemini model to use for extraction.",
    )
    api_key: str | None = Field(
        default=None,
        description="Optional API key; prefer GEMINI_API_KEY env var.",
    )
