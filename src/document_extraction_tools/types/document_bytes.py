"""Model for document bytes.

This model acts as a container for file content before any parsing occurs.
"""

from typing import Any

from pydantic import BaseModel, Field

from document_extraction_tools.types.path_identifier import PathIdentifier


class DocumentBytes(BaseModel):
    """A standardized container for raw document data in memory.

    This model decouples the extraction logic from the storage source.
    It guarantees that the processor receives raw bytes regardless of origin.
    """

    file_bytes: bytes = Field(..., description="The raw binary content of the file.")

    path_identifier: PathIdentifier = Field(
        ..., description="Path identifier for the original source."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata associated with the raw document.",
    )
