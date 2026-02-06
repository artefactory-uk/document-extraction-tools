"""Abstract Base Class for Evaluation Exporters.

This module defines the interface that all evaluation exporter implementations must satisfy.
Evaluation Exporters are responsible for taking evaluation results and persisting them
to a target destination.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.evaluation_result import EvaluationResult


class BaseEvaluationExporter(ABC):
    """Abstract interface for exporting evaluation results.

    Attributes:
        config (BaseEvaluationExporterConfig): Component-specific configuration.
        pipeline_config (EvaluationPipelineConfig | None): Optional pipeline configuration
            when constructed with a pipeline config.
    """

    config: BaseEvaluationExporterConfig
    pipeline_config: EvaluationPipelineConfig | None

    def __init__(
        self,
        config: BaseEvaluationExporterConfig | EvaluationPipelineConfig,
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseEvaluationExporterConfig | EvaluationPipelineConfig):
                Configuration specific to the evaluation exporter implementation or full pipeline configuration.
        """
        if isinstance(config, EvaluationPipelineConfig):
            self.pipeline_config = config
            self.config = config.evaluation_exporter
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    async def export(
        self,
        results: list[tuple[Document, list[EvaluationResult]]],
        context: PipelineContext | None = None,
    ) -> None:
        """Persist evaluation results to a target destination.

        This is an asynchronous operation to support non-blocking I/O writes.

        Args:
            results (list[tuple[Document, list[EvaluationResult]]]):
                A list of tuples containing documents and their associated evaluation results.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            None: The method should raise an exception if the export fails.
        """
        pass
