"""Configuration for Test Data Loader components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseTestDataLoaderConfig(BaseModel):
    """Base config for Test Data Loaders.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "test_data_loader.yaml"
