"""Model for shared pipeline context.

This model defines a shared context object that can be passed through various
pipeline components to maintain state or share information.
"""

from typing import Any

from pydantic import BaseModel, Field


class PipelineContext(BaseModel):
    """Shared context passed through pipeline components."""

    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Shared context values available across pipeline components.",
    )
