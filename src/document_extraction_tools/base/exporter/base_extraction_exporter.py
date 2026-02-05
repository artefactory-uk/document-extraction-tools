"""Abstract Base Class for Extraction Exporters.

This module defines the interface that all exporter implementations must satisfy.
Extraction Exporters are responsible for taking the extracted, structured Pydantic data
and persisting it to a target destination.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.extraction_result import (
    ExtractionResult,
    ExtractionSchema,
)


class BaseExtractionExporter(ABC):
    """Abstract interface for data persistence.

    Attributes:
        config (BaseExtractionExporterConfig): Component-specific configuration.
        pipeline_config (ExtractionPipelineConfig | None): Optional pipeline configuration
            when constructed with a pipeline config.
    """

    config: BaseExtractionExporterConfig
    pipeline_config: ExtractionPipelineConfig | None

    def __init__(
        self,
        config: BaseExtractionExporterConfig | ExtractionPipelineConfig,
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseExtractionExporterConfig | ExtractionPipelineConfig):
                Configuration specific to the exporter implementation or full pipeline configuration.
        """
        if isinstance(config, ExtractionPipelineConfig):
            self.pipeline_config = config
            self.config = config.extraction_exporter
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    async def export(
        self,
        document: Document,
        data: ExtractionResult[ExtractionSchema],
        context: PipelineContext | None = None,
    ) -> None:
        """Persists extracted data to the configured destination.

        This is an asynchronous operation to support non-blocking I/O writes.

        Args:
            document (Document): The source document for this extraction.
            data (ExtractionResult[ExtractionSchema]): The extracted data with metadata.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            None: The method should raise an exception if the export fails.
        """
        pass
