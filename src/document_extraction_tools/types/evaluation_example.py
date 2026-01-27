"""Evaluation test example model.

This model defines the input schema used by the evaluation pipeline.
"""

from typing import Generic

from pydantic import BaseModel, Field

from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.schema import ExtractionSchema


class EvaluationExample(BaseModel, Generic[ExtractionSchema]):
    """Pairs a ground-truth schema with a source document."""

    __test__ = False

    id: str = Field(..., description="Identifier for the test example.")
    path_identifier: PathIdentifier = Field(
        ..., description="Source location for the test example."
    )
    true: ExtractionSchema = Field(..., description="Ground-truth data.")
