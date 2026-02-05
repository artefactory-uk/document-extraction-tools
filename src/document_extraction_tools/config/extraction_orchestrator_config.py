"""Configuration for the Extraction Orchestrator component."""

from typing import ClassVar

from pydantic import BaseModel, Field


class ExtractionOrchestratorConfig(BaseModel):
    """Configuration for the Pipeline Orchestrator."""

    filename: ClassVar[str] = "extraction_orchestrator.yaml"

    max_workers: int = Field(
        default=4,
        description="Number of processes to use for CPU-bound tasks.",
    )

    max_concurrency: int = Field(
        default=10,
        description="Maximum number of concurrent I/O requests allowed.",
    )
