"""Domain models representing the structured document state."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Holds the actual content extracted from a single page."""

    content_type: Literal["image", "text"] = Field(
        ..., description="The type of content extracted."
    )

    data: bytes | str = Field(
        ...,
        description="The payload. For 'image', this is bytes. For 'text', this is a string.",
    )


class Page(BaseModel):
    """Represents a single page within a document."""

    page_number: int = Field(
        ..., ge=1, description="The 1-based index of the page in the original document."
    )

    content: PageContent = Field(..., description="The parsed content of this page.")


class Document(BaseModel):
    """The master object representing a fully parsed document."""

    id: str = Field(..., description="A unique identifier for this document.")

    source_path: str = Field(
        ..., description="Traceability link to the original source."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata."
    )

    pages: list[Page] = Field(
        default_factory=list,
        description="Ordered list of pages belonging to this document.",
    )
