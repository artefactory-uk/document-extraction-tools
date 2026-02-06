"""Abstract Base Class for Evaluators.

This module defines the interface that all evaluator implementations must satisfy.
Evaluators are responsible for computing evaluation metrics by comparing
predicted data against ground-truth data.
"""

from abc import ABC, abstractmethod
from typing import Generic

from document_extraction_tools.config.base_evaluator_config import BaseEvaluatorConfig
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.evaluation_result import EvaluationResult
from document_extraction_tools.types.extraction_result import (
    ExtractionResult,
    ExtractionSchema,
)


class BaseEvaluator(ABC, Generic[ExtractionSchema]):
    """Abstract interface for evaluation metrics.

    Attributes:
        config (BaseEvaluatorConfig): Component-specific configuration.
        pipeline_config (EvaluationPipelineConfig | None): Optional pipeline configuration
            when constructed with a pipeline config.
    """

    config: BaseEvaluatorConfig
    pipeline_config: EvaluationPipelineConfig | None

    def __init__(self, config: BaseEvaluatorConfig | EvaluationPipelineConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseEvaluatorConfig | EvaluationPipelineConfig):
                Configuration specific to the evaluator implementation or full pipeline configuration.
        """
        if isinstance(config, EvaluationPipelineConfig):
            self.pipeline_config = config
            self.config = self._resolve_config(config)
        else:
            self.pipeline_config = None
            self.config = config

    def _resolve_config(
        self, pipeline_config: EvaluationPipelineConfig
    ) -> BaseEvaluatorConfig:
        """Select the evaluator-specific config from the pipeline config.

        Args:
            pipeline_config (EvaluationPipelineConfig): Pipeline configuration with evaluator configs.

        Returns:
            BaseEvaluatorConfig: The config matching this evaluator.
        """
        evaluator_key = self.__class__.__name__
        config_lookup = {
            item.__class__.__name__.replace("Config", ""): item
            for item in pipeline_config.evaluators
        }
        evaluator_config = config_lookup.get(evaluator_key)
        if evaluator_config is None:
            raise ValueError(f"No configuration found for evaluator '{evaluator_key}'.")
        return evaluator_config

    @abstractmethod
    def evaluate(
        self,
        true: ExtractionResult[ExtractionSchema],
        pred: ExtractionResult[ExtractionSchema],
        context: PipelineContext | None = None,
    ) -> EvaluationResult:
        """Compute a metric for a single document.

        Args:
            true (ExtractionResult[ExtractionSchema]): Ground-truth data with metadata.
            pred (ExtractionResult[ExtractionSchema]): Predicted data with metadata.
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            EvaluationResult: The metric result for this document.
        """
        pass
