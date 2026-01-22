"""Domain models representing the structured document state."""

from typing import Any, Literal, TypeAlias

import numpy as np
from PIL import Image as PILImage
from pydantic import BaseModel, ConfigDict, Field, model_validator

from document_extraction_tools.types.path_identifier import PathIdentifier

PILImageType: TypeAlias = PILImage.Image
NumpyArrayType: TypeAlias = np.ndarray


class TextData(BaseModel):
    """Encapsulates textual content."""

    content: str = Field(..., description="The extracted text string.")


class ImageData(BaseModel):
    """Encapsulates image content in various formats."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    content: bytes | PILImageType | NumpyArrayType = Field(
        ...,
        description="The image payload. Can be raw bytes, a PIL Image, or a NumPy array.",
    )


class Page(BaseModel):
    """Represents a single page within a document."""

    page_number: int = Field(
        ..., ge=1, description="The 1-based index of the page in the original document."
    )

    data: ImageData | TextData = Field(
        ...,
        description="The payload for the page.",
    )


class Document(BaseModel):
    """The master object representing a fully parsed document."""

    id: str = Field(..., description="A unique identifier for this document.")

    content_type: Literal["image", "text"] = Field(
        ..., description="The type of content extracted."
    )

    pages: list[Page] = Field(
        default_factory=list,
        description="Ordered list of pages belonging to this document.",
    )

    path_identifier: PathIdentifier = Field(
        ..., description="Traceability link to the original source."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata."
    )

    @model_validator(mode="after")
    def check_content_consistency(self) -> "Document":
        """Ensures page data types match the declared content_type."""
        expected_type = ImageData if self.content_type == "image" else TextData

        for page in self.pages:
            if not isinstance(page.data, expected_type):
                raise ValueError(
                    f"Document declared as '{self.content_type}' but Page {page.page_number} "
                    f"contains incompatible '{type(page.data).__name__}'."
                )

        return self
