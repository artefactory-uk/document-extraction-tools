"""Master Evaluation Pipeline Configuration."""

from pydantic import BaseModel, Field

from document_extraction_tools.config.base_converter_config import BaseConverterConfig
from document_extraction_tools.config.base_evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.config.base_evaluator_config import BaseEvaluatorConfig
from document_extraction_tools.config.base_extractor_config import BaseExtractorConfig
from document_extraction_tools.config.base_reader_config import BaseReaderConfig
from document_extraction_tools.config.base_test_data_loader_config import (
    BaseTestDataLoaderConfig,
)
from document_extraction_tools.config.evaluation_orchestrator_config import (
    EvaluationOrchestratorConfig,
)


class EvaluationPipelineConfig(BaseModel):
    """Master container for evaluation pipeline component configurations.

    This class aggregates the configurations for all evaluation pipeline components.
    """

    orchestrator: EvaluationOrchestratorConfig = Field(
        ..., description="Configuration for orchestrating evaluation execution."
    )

    test_data_loader: BaseTestDataLoaderConfig = Field(
        ..., description="Configuration for loading evaluation examples."
    )

    evaluators: list[BaseEvaluatorConfig] = Field(
        ..., description="Evaluator configurations to apply."
    )

    reader: BaseReaderConfig = Field(
        ..., description="Configuration for reading raw document bytes."
    )

    converter: BaseConverterConfig = Field(
        ..., description="Configuration for converting raw bytes into documents."
    )

    extractor: BaseExtractorConfig = Field(
        ..., description="Configuration for extracting structured data."
    )

    evaluation_exporter: BaseEvaluationExporterConfig = Field(
        ..., description="Configuration for exporting evaluation results."
    )
