"""Model for extraction results.

This model wraps extracted data along with optional metadata.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

ExtractionSchema = TypeVar("ExtractionSchema", bound=BaseModel)


class ExtractionResult(BaseModel, Generic[ExtractionSchema]):
    """Wraps an extraction schema with optional metadata."""

    data: ExtractionSchema

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata associated with the extraction result.",
    )
