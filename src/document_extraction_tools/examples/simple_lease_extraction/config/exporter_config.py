"""Configuration for the example exporter."""

from pydantic import Field

from document_extraction_tools.config.exporter_config import BaseExporterConfig
from document_extraction_tools.types.path_identifier import PathIdentifier


class ExporterConfig(BaseExporterConfig):
    """Configuration for JSON export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where exported files will be saved.",
    )
