"""Example entrypoint for the simple lease evaluation pipeline."""

import asyncio
import logging
from pathlib import Path

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
from .components.test_data_loader.local_test_data_loader import LocalTestDataLoader
from .config.converter_config import ConverterConfig
from .config.evaluation_exporter_config import EvaluationExporterConfig
from .config.evaluator_config import AccuracyEvaluatorConfig, F1EvaluatorConfig
from .config.extractor_config import ExtractorConfig
from .config.reader_config import ReaderConfig
from .config.test_data_loader_config import TestDataLoaderConfig
from .schema.schema import SimpleLeaseDetails

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the example evaluation pipeline."""
    # 1. Load Configuration
    config_path = Path(__file__).parent / "config"
    cfg: EvaluationPipelineConfig = load_evaluation_config(
        config_dir=config_path,
        orchestrator_config_cls=EvaluationOrchestratorConfig,
        test_data_loader_config_cls=TestDataLoaderConfig,
        evaluator_config_classes=[AccuracyEvaluatorConfig, F1EvaluatorConfig],
        reader_config_cls=ReaderConfig,
        converter_config_cls=ConverterConfig,
        extractor_config_cls=ExtractorConfig,
        evaluation_exporter_config_cls=EvaluationExporterConfig,
    )

    logger.info("Configuration loaded successfully.")

    # 2. Initialize Orchestrator
    orchestrator: EvaluationOrchestrator = EvaluationOrchestrator.from_config(
        config=cfg,
        schema=SimpleLeaseDetails,
        reader_cls=LocalFileReader,
        converter_cls=PDFToImageConverter,
        extractor_cls=GeminiImageExtractor,
        test_data_loader_cls=LocalTestDataLoader,
        evaluator_classes=[AccuracyEvaluator, F1Evaluator],
        evaluation_exporter_cls=LocalFileEvaluationExporter,
    )

    # 3. Load Evaluation Examples
    loader_path = PathIdentifier(path=cfg.test_data_loader.test_data.path)
    examples: list[TestExample] = orchestrator.test_data_loader.load_test_data(
        loader_path
    )

    logger.info(f"Loaded {len(examples)} evaluation examples.")

    # 4. Run Evaluation
    asyncio.run(orchestrator.run(examples))


if __name__ == "__main__":
    main()
