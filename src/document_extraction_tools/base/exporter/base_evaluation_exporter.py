"""Abstract Base Class for Evaluation Exporters.

This module defines the interface that all evaluation exporter implementations must satisfy.
Evaluation Exporters are responsible for taking evaluation results and persisting them
to a target destination.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.evaluation_result import EvaluationResult


class BaseEvaluationExporter(ABC):
    """Abstract interface for exporting evaluation results."""

    def __init__(self, config: BaseEvaluationExporterConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseEvaluationExporterConfig): Configuration specific to the evaluation exporter implementation.
        """
        self.config = config

    @abstractmethod
    async def export(self, document: Document, results: list[EvaluationResult]) -> None:
        """Persist evaluation results to a target destination.

        This is an asynchronous operation to support non-blocking I/O writes.

        Args:
            document (Document): The source document for these results.
            results (list[EvaluationResult]): A list of evaluation results to be exported.

        Returns:
            None: The method should raise an exception if the export fails.
        """
        pass
