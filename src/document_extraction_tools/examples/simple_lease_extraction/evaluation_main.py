"""Example entrypoint for the simple lease evaluation pipeline."""

import asyncio
import logging
from pathlib import Path

import mlflow
from mlflow.entities.span import LiveSpan

from document_extraction_tools.config.config_loader import load_evaluation_config
from document_extraction_tools.config.evaluation_orchestrator_config import (
    EvaluationOrchestratorConfig,
)
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.runners.evaluation.evaluation_orchestrator import (
    EvaluationOrchestrator,
)
from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.test_example import TestExample

from .components.converter.pdf_to_image_converter import PDFToImageConverter
from .components.evaluator.accuracy_evaluator import AccuracyEvaluator
from .components.evaluator.f1_evaluator import F1Evaluator
from .components.exporter.local_file_evaluation_exporter import (
    LocalFileEvaluationExporter,
)
from .components.extractor.gemini_image_extractor import GeminiImageExtractor
from .components.reader.local_file_reader import LocalFileReader
from .components.test_data_loader.local_json_test_data_loader import (
    LocalJSONTestDataLoader,
)
from .config.evaluator_config import AccuracyEvaluatorConfig, F1EvaluatorConfig
from .config.gemini_image_extractor_config import GeminiImageExtractorConfig
from .config.local_file_evaluation_exporter_config import (
    LocalFileEvaluationExporterConfig,
)
from .config.local_file_reader_config import LocalFileReaderConfig
from .config.local_json_test_data_loader_config import LocalJSONTestDataLoaderConfig
from .config.pdf_to_image_converter_config import PDFToImageConverterConfig
from .schema.schema import SimpleLeaseDetails
from .utils.mlflow_utils import setup_mlflow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


@mlflow.trace(name="run_evaluation_pipeline", span_type="CHAIN")
def run_evaluation_pipeline(config_dir: Path) -> dict[str, int]:
    """Run the example evaluation pipeline."""
    span = mlflow.get_current_active_span()
    if span is not None:
        span.set_inputs({"config_dir": str(config_dir)})

    # 1. Load Configuration
    cfg: EvaluationPipelineConfig = load_evaluation_config(
        config_dir=config_dir,
        orchestrator_config_cls=EvaluationOrchestratorConfig,
        test_data_loader_config_cls=LocalJSONTestDataLoaderConfig,
        evaluator_config_classes=[AccuracyEvaluatorConfig, F1EvaluatorConfig],
        reader_config_cls=LocalFileReaderConfig,
        converter_config_cls=PDFToImageConverterConfig,
        extractor_config_cls=GeminiImageExtractorConfig,
        evaluation_exporter_config_cls=LocalFileEvaluationExporterConfig,
    )

    logger.info("Configuration loaded successfully.")

    # 2. Initialize Orchestrator
    orchestrator: EvaluationOrchestrator = EvaluationOrchestrator.from_config(
        config=cfg,
        schema=SimpleLeaseDetails,
        reader_cls=LocalFileReader,
        converter_cls=PDFToImageConverter,
        extractor_cls=GeminiImageExtractor,
        test_data_loader_cls=LocalJSONTestDataLoader,
        evaluator_classes=[AccuracyEvaluator, F1Evaluator],
        evaluation_exporter_cls=LocalFileEvaluationExporter,
    )

    # 3. Load Evaluation Examples
    loader_path = PathIdentifier(path=cfg.test_data_loader.test_data.path)
    examples: list[TestExample] = orchestrator.test_data_loader.load_test_data(
        loader_path
    )

    logger.info("Loaded %d evaluation examples.", len(examples))

    # 4. Run Evaluation
    asyncio.run(orchestrator.run(examples))

    return {"examples_processed": len(examples)}


if __name__ == "__main__":
    # Decorate orchestrator methods with MLflow tracing
    traced_process_example = mlflow.trace(name="process_example", span_type="CHAIN")(
        EvaluationOrchestrator.process_example
    )
    setattr(EvaluationOrchestrator, "process_example", traced_process_example)

    # Silent overly verbose logs from dependencies
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)

    # Set up MLflow tracking
    setup_mlflow(
        tracking_uri="http://localhost:8080", experiment_name="simple_lease_evaluation"
    )

    def _drop_process_example_outputs(span: LiveSpan) -> None:
        """Span processor to drop outputs from process_example spans."""
        if span.name == "process_example":
            span.set_outputs(None)

    mlflow.tracing.configure(span_processors=[_drop_process_example_outputs])

    # Run the evaluation pipeline with the config directory
    config_dir = Path(__file__).parent / "config/yaml"
    with mlflow.start_run():
        run_evaluation_pipeline(config_dir)
