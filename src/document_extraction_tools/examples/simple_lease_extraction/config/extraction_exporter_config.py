"""Configuration for the example extraction exporter."""

from pydantic import Field

from document_extraction_tools.config.base_extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class ExporterConfig(BaseExtractionExporterConfig):
    """Configuration for JSON export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where exported files will be saved.",
    )
