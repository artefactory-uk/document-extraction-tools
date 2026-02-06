"""Abstract Base Class for Document Converters.

This module defines the interface that all converter implementations must satisfy.
Converters are responsible for transforming raw binary data (DocumentBytes)
into a structured Document object containing pages and content.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_converter_config import BaseConverterConfig
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.document_bytes import DocumentBytes


class BaseConverter(ABC):
    """Abstract interface for document transformation.

    Attributes:
        config (BaseConverterConfig): Component-specific configuration.
        pipeline_config (ExtractionPipelineConfig | EvaluationPipelineConfig | None):
            Optional pipeline configuration when constructed with a pipeline config.
    """

    config: BaseConverterConfig
    pipeline_config: ExtractionPipelineConfig | EvaluationPipelineConfig | None

    def __init__(
        self,
        config: (
            BaseConverterConfig | ExtractionPipelineConfig | EvaluationPipelineConfig
        ),
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseConverterConfig | ExtractionPipelineConfig | EvaluationPipelineConfig):
                Configuration specific to the converter implementation or full pipeline configuration.
        """
        if isinstance(config, (ExtractionPipelineConfig, EvaluationPipelineConfig)):
            self.pipeline_config = config
            self.config = config.converter
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    def convert(
        self, document_bytes: DocumentBytes, context: PipelineContext | None = None
    ) -> Document:
        """Transforms raw document bytes into a structured Document object.

        This method should handle the parsing logic and map the metadata from the
        input bytes to the output document.

        Args:
            document_bytes (DocumentBytes): The standardized raw input containing
                                            file bytes and source metadata.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            Document: The fully structured document model ready for extraction.
        """
        pass
