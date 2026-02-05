"""Configuration for the Evaluation Orchestrator component."""

from typing import ClassVar

from pydantic import BaseModel, Field


class EvaluationOrchestratorConfig(BaseModel):
    """Configuration for the Evaluation Orchestrator."""

    filename: ClassVar[str] = "evaluation_orchestrator.yaml"

    max_workers: int = Field(
        default=4,
        description="Number of processes to use for CPU-bound tasks.",
    )

    max_concurrency: int = Field(
        default=10,
        description="Maximum number of concurrent I/O requests allowed.",
    )
