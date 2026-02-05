"""Abstract Base Class for Test Data Loaders.

This module defines the interface that all test data loader implementations must satisfy.
Test Data Loaders are responsible for loading evaluation test examples from a specified source.
"""

from abc import ABC, abstractmethod
from typing import Generic

from document_extraction_tools.config.base_test_data_loader_config import (
    BaseTestDataLoaderConfig,
)
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.evaluation_example import EvaluationExample
from document_extraction_tools.types.extraction_result import ExtractionSchema
from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseTestDataLoader(ABC, Generic[ExtractionSchema]):
    """Abstract interface for loading evaluation test data.

    Attributes:
        config (BaseTestDataLoaderConfig): Component-specific configuration.
        pipeline_config (EvaluationPipelineConfig | None): Optional pipeline configuration
            when constructed with a pipeline config.
    """

    config: BaseTestDataLoaderConfig
    pipeline_config: EvaluationPipelineConfig | None

    def __init__(
        self,
        config: BaseTestDataLoaderConfig | EvaluationPipelineConfig,
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseTestDataLoaderConfig | EvaluationPipelineConfig):
                Configuration specific to the test data loader implementation or full pipeline configuration.
        """
        if isinstance(config, EvaluationPipelineConfig):
            self.pipeline_config = config
            self.config = config.test_data_loader
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    def load_test_data(
        self,
        path_identifier: PathIdentifier,
        context: PipelineContext | None = None,
    ) -> list[EvaluationExample[ExtractionSchema]]:
        """Load test examples for evaluation.

        This method should retrieve and return a list of EvaluationExample instances
        based on the provided path identifier.

        Args:
            path_identifier (PathIdentifier): The source location for loading evaluation examples.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            list[EvaluationExample[ExtractionSchema]]: A list of evaluation examples for evaluation.
        """
        pass
