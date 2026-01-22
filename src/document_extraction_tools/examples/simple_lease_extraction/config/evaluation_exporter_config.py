"""Configuration for the example evaluation exporter."""

from pydantic import Field

from document_extraction_tools.config.evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class EvaluationExporterConfig(BaseEvaluationExporterConfig):
    """Configuration for evaluation results export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where evaluation results will be saved.",
    )
