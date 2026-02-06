"""Abstract Base Class for Document Readers.

This module defines the interface that all reader implementations must satisfy.
Readers are responsible for fetching raw file content from a source
and returning it as a standardized DocumentBytes object.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_reader_config import BaseReaderConfig
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.document_bytes import DocumentBytes
from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseReader(ABC):
    """Abstract interface for document ingestion.

    Attributes:
        config (BaseReaderConfig): Component-specific configuration.
        pipeline_config (ExtractionPipelineConfig | EvaluationPipelineConfig | None):
            Optional pipeline configuration when constructed with a pipeline config.
    """

    config: BaseReaderConfig
    pipeline_config: ExtractionPipelineConfig | EvaluationPipelineConfig | None

    def __init__(
        self,
        config: BaseReaderConfig | ExtractionPipelineConfig | EvaluationPipelineConfig,
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseReaderConfig | ExtractionPipelineConfig | EvaluationPipelineConfig):
                Configuration specific to the reader implementation or full pipeline configuration.
        """
        if isinstance(config, (ExtractionPipelineConfig, EvaluationPipelineConfig)):
            self.pipeline_config = config
            self.config = config.reader
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    def read(
        self, path_identifier: PathIdentifier, context: PipelineContext | None = None
    ) -> DocumentBytes:
        """Reads a document from a specific source and returns its raw bytes.

        Args:
            path_identifier (PathIdentifier): The identifier for the file.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            DocumentBytes: A standardized container with raw bytes and source metadata.
        """
        pass
