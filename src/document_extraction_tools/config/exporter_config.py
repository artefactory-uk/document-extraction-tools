"""Configuration for Exporter components."""

from pydantic import BaseModel, Field

from document_extraction_tools.types.path_identifier import PathIdentifier


class ExporterConfig(BaseModel):
    """Configuration for Exporters."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where exported files will be saved.",
    )
