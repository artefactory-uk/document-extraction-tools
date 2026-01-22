"""Configuration for Extraction Exporter components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseExtractionExporterConfig(BaseModel):
    """Base config for Exporters.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "extraction_exporter.yaml"
