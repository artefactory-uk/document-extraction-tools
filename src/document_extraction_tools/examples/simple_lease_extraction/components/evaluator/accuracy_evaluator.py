"""Accuracy evaluator for the example schema."""

from document_extraction_tools.base.evaluator.base_evaluator import BaseEvaluator
from document_extraction_tools.examples.simple_lease_extraction.config.evaluator_config import (
    AccuracyEvaluatorConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.types.evaluation_result import EvaluationResult


class AccuracyEvaluator(BaseEvaluator[SimpleLeaseDetails]):
    """Computes field-level exact match accuracy."""

    def __init__(self, config: AccuracyEvaluatorConfig) -> None:
        """Initialize the accuracy evaluator with a configuration."""
        super().__init__(config)

    def evaluate(
        self, true: SimpleLeaseDetails, pred: SimpleLeaseDetails
    ) -> EvaluationResult:
        """Compute field-level exact match accuracy."""
        true_data = true.model_dump()
        pred_data = pred.model_dump()

        total = len(true_data)
        matches = sum(
            1 for key, value in true_data.items() if pred_data.get(key) == value
        )
        accuracy = matches / total if total else 0.0

        return EvaluationResult(
            name="accuracy",
            result=accuracy,
            description=f"Field-level exact match accuracy ({matches}/{total}).",
        )
