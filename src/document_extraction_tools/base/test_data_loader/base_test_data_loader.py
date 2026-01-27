"""Abstract Base Class for Test Data Loaders.

This module defines the interface that all test data loader implementations must satisfy.
Test Data Loaders are responsible for loading evaluation test examples from a specified source.
"""

from abc import ABC, abstractmethod
from typing import Generic

from document_extraction_tools.config.base_test_data_loader_config import (
    BaseTestDataLoaderConfig,
)
from document_extraction_tools.types.evaluation_example import EvaluationExample
from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.schema import ExtractionSchema


class BaseTestDataLoader(ABC, Generic[ExtractionSchema]):
    """Abstract interface for loading evaluation test data."""

    def __init__(self, config: BaseTestDataLoaderConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseTestDataLoaderConfig): Configuration specific to the test data loader implementation.
        """
        self.config = config

    @abstractmethod
    def load_test_data(
        self, path_identifier: PathIdentifier
    ) -> list[EvaluationExample[ExtractionSchema]]:
        """Load test examples for evaluation.

        This method should retrieve and return a list of EvaluationExample instances
        based on the provided path identifier.

        Args:
            path_identifier (PathIdentifier): The source location for loading evaluation examples.

        Returns:
            list[EvaluationExample[ExtractionSchema]]: A list of evaluation examples for evaluation.
        """
        pass
