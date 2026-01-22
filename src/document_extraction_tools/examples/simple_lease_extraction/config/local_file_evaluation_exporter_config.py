"""Configuration for the local file evaluation exporter."""

from pydantic import Field

from document_extraction_tools.config.base_evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class LocalFileEvaluationExporterConfig(BaseEvaluationExporterConfig):
    """Configuration for local evaluation results export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where evaluation results will be saved.",
    )
