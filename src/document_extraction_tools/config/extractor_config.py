"""Configuration for Extractor components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseExtractorConfig(BaseModel):
    """Base config for Extractors.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "extractor.yaml"
