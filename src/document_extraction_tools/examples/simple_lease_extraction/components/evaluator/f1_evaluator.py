"""F1 evaluator for the example schema."""

from document_extraction_tools.base.evaluator.evaluator import BaseEvaluator
from document_extraction_tools.examples.simple_lease_extraction.config.evaluator_config import (
    F1EvaluatorConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.types.evaluation_result import EvaluationResult


class F1Evaluator(BaseEvaluator[SimpleLeaseDetails]):
    """Computes field-level F1 score."""

    def __init__(self, config: F1EvaluatorConfig) -> None:
        """Initialize the F1 evaluator with a configuration."""
        super().__init__(config)

    def evaluate(
        self, true: SimpleLeaseDetails, pred: SimpleLeaseDetails
    ) -> EvaluationResult:
        """Compute field-level F1 score."""
        true_data = true.model_dump()
        pred_data = pred.model_dump()

        tp = fp = fn = 0
        for key, true_value in true_data.items():
            pred_value = pred_data.get(key)
            if true_value is None and pred_value is None:
                continue
            if pred_value == true_value and true_value is not None:
                tp += 1
                continue
            if pred_value is not None and pred_value != true_value:
                fp += 1
            if true_value is not None and pred_value != true_value:
                fn += 1

        denom = (2 * tp) + fp + fn
        f1 = (2 * tp / denom) if denom else 0.0

        return EvaluationResult(
            name="f1",
            result=f1,
            description=f"Field-level F1 score (tp={tp}, fp={fp}, fn={fn}).",
        )
