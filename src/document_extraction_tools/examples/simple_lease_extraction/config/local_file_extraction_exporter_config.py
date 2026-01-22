"""Configuration for the local file extraction exporter."""

from pydantic import Field

from document_extraction_tools.config.base_extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class LocalFileExtractionExporterConfig(BaseExtractionExporterConfig):
    """Configuration for local file extraction export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where exported files will be saved.",
    )
