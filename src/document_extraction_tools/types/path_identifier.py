"""Models for identifying the source of a document."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PathIdentifier(BaseModel):
    """A unified reference to a document source."""

    path: str | Path = Field(..., description="The primary path identifier.")

    context: dict[str, Any] = Field(
        default_factory=dict, description="Optional execution context."
    )
