"""Configuration for Reader components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseReaderConfig(BaseModel):
    """Base config for Readers.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "reader.yaml"
