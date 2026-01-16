"""Input models representing raw data ingestion.

These models act as containers for file content before any parsing occurs.
"""

from pydantic import BaseModel, Field


class DocumentBytes(BaseModel):
    """A standardized container for raw document data in memory.

    This model decouples the extraction logic from the storage source.
    It guarantees that the processor receives raw bytes regardless of origin.
    """

    filename: str = Field(..., description="The name of the file.")

    file_bytes: bytes = Field(..., description="The raw binary content of the file.")

    original_source: str = Field(
        ..., description="The name of the source where this file originated."
    )

    mime_type: str = Field(
        default="application/pdf",
        description="The standard MIME type of the file content.",
    )
