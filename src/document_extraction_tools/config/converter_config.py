"""Configuration for Converter components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseConverterConfig(BaseModel):
    """Base config for Converters.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "converter.yaml"
