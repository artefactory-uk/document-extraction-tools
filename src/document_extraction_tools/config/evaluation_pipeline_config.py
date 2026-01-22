"""Master Evaluation Pipeline Configuration."""

from pydantic import BaseModel

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

    orchestrator: EvaluationOrchestratorConfig
    test_data_loader: BaseTestDataLoaderConfig
    evaluators: list[BaseEvaluatorConfig]
    reader: BaseReaderConfig
    converter: BaseConverterConfig
    extractor: BaseExtractorConfig
    evaluation_exporter: BaseEvaluationExporterConfig
