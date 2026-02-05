"""Abstract Base Class for Information Extractors.

This module defines the interface that all extractor implementations must satisfy.
Extractors are responsible for analyzing the structured Document
and populating a target Pydantic schema with specific data points.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_extractor_config import BaseExtractorConfig
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
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


class BaseExtractor(ABC):
    """Abstract interface for data extraction.

    Attributes:
        config (BaseExtractorConfig): Component-specific configuration.
        pipeline_config (ExtractionPipelineConfig | EvaluationPipelineConfig | None):
            Optional pipeline configuration when constructed with a pipeline config.
    """

    config: BaseExtractorConfig
    pipeline_config: ExtractionPipelineConfig | EvaluationPipelineConfig | None

    def __init__(
        self,
        config: (
            BaseExtractorConfig | ExtractionPipelineConfig | EvaluationPipelineConfig
        ),
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseExtractorConfig | ExtractionPipelineConfig | EvaluationPipelineConfig):
                Configuration specific to the extractor implementation or full pipeline configuration.
        """
        if isinstance(config, (ExtractionPipelineConfig, EvaluationPipelineConfig)):
            self.pipeline_config = config
            self.config = config.extractor
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    async def extract(
        self,
        document: Document,
        schema: type[ExtractionSchema],
        context: PipelineContext | None = None,
    ) -> ExtractionResult[ExtractionSchema]:
        """Extracts structured data from a Document to match the provided Schema.

        This is an asynchronous operation to support I/O-bound tasks.

        Args:
            document (Document): The fully parsed document.
            schema (type[ExtractionSchema]): The Pydantic model class defining the target structure.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            ExtractionResult[ExtractionSchema]: The extracted data with metadata.
        """
        pass
