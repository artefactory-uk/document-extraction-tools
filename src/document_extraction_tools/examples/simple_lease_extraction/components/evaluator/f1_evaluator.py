"""F1 evaluator for the example schema."""

from document_extraction_tools.base.evaluator.base_evaluator import BaseEvaluator
from document_extraction_tools.examples.simple_lease_extraction.config.evaluator_config import (
    F1EvaluatorConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.examples.simple_lease_extraction.utils.llm_as_a_judge import (
    get_llm_judge_client,
    invoke_llm_as_a_judge,
)
from document_extraction_tools.types.evaluation_result import EvaluationResult


class F1Evaluator(BaseEvaluator[SimpleLeaseDetails]):
    """Computes field-level F1 score."""

    def __init__(self, config: F1EvaluatorConfig) -> None:
        """Initialize the F1 evaluator with a configuration."""
        super().__init__(config)
        self._llm_client = get_llm_judge_client() if self.config.use_llm_judge else None

    def _values_equal(self, true_value: object, pred_value: object) -> bool:
        if self.config.use_llm_judge:
            return invoke_llm_as_a_judge(true_value, pred_value, self._llm_client)
        return pred_value == true_value

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
            is_match = self._values_equal(true_value, pred_value)
            if is_match and true_value is not None:
                tp += 1
                continue
            if pred_value is not None and not is_match:
                fp += 1
            if true_value is not None and not is_match:
                fn += 1

        denom = (2 * tp) + fp + fn
        f1 = (2 * tp / denom) if denom else 0.0

        return EvaluationResult(
            name="f1",
            result=f1,
            description=f"Field-level F1 score (tp={tp}, fp={fp}, fn={fn}).",
        )
