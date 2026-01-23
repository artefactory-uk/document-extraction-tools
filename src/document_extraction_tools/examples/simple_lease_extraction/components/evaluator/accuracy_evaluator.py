"""Accuracy evaluator for the example schema."""

from document_extraction_tools.base.evaluator.base_evaluator import BaseEvaluator
from document_extraction_tools.examples.simple_lease_extraction.config.evaluator_config import (
    AccuracyEvaluatorConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.examples.simple_lease_extraction.utils.llm_as_a_judge import (
    get_llm_judge_client,
    invoke_llm_as_a_judge,
)
from document_extraction_tools.types.evaluation_result import EvaluationResult


class AccuracyEvaluator(BaseEvaluator[SimpleLeaseDetails]):
    """Computes field-level exact match accuracy."""

    def __init__(self, config: AccuracyEvaluatorConfig) -> None:
        """Initialize the accuracy evaluator with a configuration."""
        super().__init__(config)
        self._llm_client = get_llm_judge_client() if self.config.use_llm_judge else None

    def _values_equal(self, true_value: object, pred_value: object) -> bool:
        if self.config.use_llm_judge:
            return invoke_llm_as_a_judge(true_value, pred_value, self._llm_client)
        return pred_value == true_value

    def evaluate(
        self, true: SimpleLeaseDetails, pred: SimpleLeaseDetails
    ) -> EvaluationResult:
        """Compute field-level exact match accuracy."""
        true_data = true.model_dump()
        pred_data = pred.model_dump()

        total = len(true_data)
        matches = sum(
            1
            for key, value in true_data.items()
            if self._values_equal(value, pred_data.get(key))
        )
        accuracy = matches / total if total else 0.0

        return EvaluationResult(
            name="accuracy",
            result=accuracy,
            description=f"Field-level exact match accuracy ({matches}/{total}).",
        )
