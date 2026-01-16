"""Base configuration for Exporter components."""

from pydantic import BaseModel, Field

from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseExporterConfig(BaseModel):
    """Configuration for Exporters.

    Implementations should subclass this to add specific parameters.
    """

    destination: PathIdentifier = Field(
        ...,
        description="The root destination for exports.",
    )
