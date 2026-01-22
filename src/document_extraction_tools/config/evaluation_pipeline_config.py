"""Master Evaluation Pipeline Configuration."""

from pydantic import BaseModel

from document_extraction_tools.config.converter_config import BaseConverterConfig
from document_extraction_tools.config.evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.config.evaluation_orchestrator_config import (
    EvaluationOrchestratorConfig,
)
from document_extraction_tools.config.evaluator_config import BaseEvaluatorConfig
from document_extraction_tools.config.extractor_config import BaseExtractorConfig
from document_extraction_tools.config.reader_config import BaseReaderConfig
from document_extraction_tools.config.test_data_loader_config import (
    BaseTestDataLoaderConfig,
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
