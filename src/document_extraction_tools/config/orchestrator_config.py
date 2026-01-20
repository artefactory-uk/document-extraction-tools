"""Configuration for the Orchestrator component."""

from pydantic import BaseModel, Field


class OrchestratorConfig(BaseModel):
    """Configuration for the Pipeline Orchestrator."""

    max_workers: int = Field(
        default=4,
        description="Number of processes to use for CPU-bound tasks.",
    )
    max_concurrency: int = Field(
        default=10,
        description="Maximum number of concurrent I/O requests allowed.",
    )
