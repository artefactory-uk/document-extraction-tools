"""Configuration for Exporter components."""

from pydantic import BaseModel


class BaseExporterConfig(BaseModel):
    """Base config for Exporters.

    Implementations should subclass this to add specific parameters.
    """
