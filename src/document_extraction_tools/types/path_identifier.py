"""Model for path identifiers.

This model provides a unified way to reference document sources
using paths, along with optional metadata.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PathIdentifier(BaseModel):
    """A unified reference to a document source."""

    path: str | Path = Field(..., description="The primary path identifier.")

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata associated with the path identifier.",
    )
