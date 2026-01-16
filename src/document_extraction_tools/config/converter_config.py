"""Base configuration for Converter components."""

from pydantic import BaseModel


class BaseConverterConfig(BaseModel):
    """Base config for Converters.

    Implementations should subclass this to add specific parameters.
    """

    pass
