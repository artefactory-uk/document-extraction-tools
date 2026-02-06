"""Model for evaluation examples.

This model defines the input schema used by the evaluation pipeline.
"""

from typing import Any, Generic

from pydantic import BaseModel, Field

from document_extraction_tools.types.extraction_result import (
    ExtractionResult,
    ExtractionSchema,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class EvaluationExample(BaseModel, Generic[ExtractionSchema]):
    """Pairs a ground-truth schema with a source document."""

    id: str = Field(..., description="Identifier for the test example.")

    path_identifier: PathIdentifier = Field(
        ..., description="Source location for the test example."
    )

    true: ExtractionResult[ExtractionSchema] = Field(
        ..., description="Ground-truth data with metadata."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata associated with the evaluation example.",
    )
