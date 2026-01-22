"""Example entrypoint for the simple lease extraction pipeline."""

import asyncio
import logging
from pathlib import Path

from document_extraction_tools.config.config_loader import load_config
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.runners.extraction.orchestrator import (
    ExtractionOrchestrator,
)
from document_extraction_tools.types.path_identifier import PathIdentifier

from .components.converter.pdf_to_image_converter import PDFToImageConverter
from .components.exporter.local_file_extraction_exporter import (
    LocalFileExtractionExporter,
)
from .components.extractor.gemini_image_extractor import GeminiImageExtractor
from .components.file_lister.local_file_lister import LocalFileLister
from .components.reader.local_file_reader import LocalFileReader
from .config.converter_config import ConverterConfig
from .config.extraction_exporter_config import ExporterConfig
from .config.extractor_config import ExtractorConfig
from .config.file_lister_config import FileListerConfig
from .config.reader_config import ReaderConfig
from .schema.schema import SimpleLeaseDetails

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the example extraction pipeline."""
    # 1. Load Configuration
    config_path = str(Path(__file__).parent / "config")
    cfg: ExtractionPipelineConfig = load_config(
        config_dir=config_path,
        lister_cls=FileListerConfig,
        reader_cls=ReaderConfig,
        converter_cls=ConverterConfig,
        extractor_cls=ExtractorConfig,
        exporter_cls=ExporterConfig,
    )

    logger.info("Configuration loaded successfully.")

    # 2. Initialize Orchestrator
    orchestrator: ExtractionOrchestrator = ExtractionOrchestrator.from_config(
        config=cfg,
        schema=SimpleLeaseDetails,
        reader_cls=LocalFileReader,
        converter_cls=PDFToImageConverter,
        extractor_cls=GeminiImageExtractor,
        exporter_cls=LocalFileExtractionExporter,
    )

    # 3. List Files to Process
    lister: LocalFileLister = LocalFileLister(cfg.file_lister)
    files: list[PathIdentifier] = lister.list_files()

    logger.info(f"Found {len(files)} files to process.")

    # 4. Run Extraction
    asyncio.run(orchestrator.run(files))


if __name__ == "__main__":
    main()
