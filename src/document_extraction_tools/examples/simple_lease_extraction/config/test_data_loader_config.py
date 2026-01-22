"""Configuration for the example test data loader."""

from pydantic import Field

from document_extraction_tools.config.base_test_data_loader_config import (
    BaseTestDataLoaderConfig,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class TestDataLoaderConfig(BaseTestDataLoaderConfig):
    """Configuration for loading evaluation test data."""

    test_data: PathIdentifier = Field(
        ..., description="Path to the test data JSON file."
    )
