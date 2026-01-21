"""Configuration for Exporter components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseExporterConfig(BaseModel):
    """Base config for Exporters.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "exporter.yaml"
