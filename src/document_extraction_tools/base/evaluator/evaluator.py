"""Abstract Base Class for Evaluators.

This module defines the interface that all evaluator implementations must satisfy.
Evaluators are responsible for computing evaluation metrics by comparing
predicted data against ground-truth data.
"""

from abc import ABC, abstractmethod
from typing import Generic

from document_extraction_tools.types.evaluation_result import EvaluationResult
from document_extraction_tools.types.schema import ExtractionSchema


class BaseEvaluator(ABC, Generic[ExtractionSchema]):
    """Abstract interface for evaluation metrics."""

    # TODO: Add name in init and config based on the name to init params like llm etc.
    @abstractmethod
    def evaluate(
        self, true: ExtractionSchema, pred: ExtractionSchema
    ) -> EvaluationResult:
        """Compute a metric for a single document.

        Args:
            true (ExtractionSchema): Ground-truth data.
            pred (ExtractionSchema): Predicted data.

        Returns:
            EvaluationResult: The metric result for this document.
        """
        pass
