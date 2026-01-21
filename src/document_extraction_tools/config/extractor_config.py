"""Configuration for Extractor components."""

from pydantic import BaseModel


class BaseExtractorConfig(BaseModel):
    """Base config for Extractors.

    Implementations should subclass this to add specific parameters.
    """
