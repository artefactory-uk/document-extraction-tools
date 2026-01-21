"""Example entrypoint for the simple lease extraction pipeline."""

import asyncio
import logging
from pathlib import Path

from document_extraction_tools.config.config_loader import load_config
from document_extraction_tools.examples.simple_lease_extraction.components.converter.pdf_to_image_converter import (
    PDFToImageConverter,
)
from document_extraction_tools.examples.simple_lease_extraction.components.exporter.local_file_exporter import (
    LocalFileExporter,
)
from document_extraction_tools.examples.simple_lease_extraction.components.extractor.gemini_image_extractor import (
    GeminiImageExtractor,
)
from document_extraction_tools.examples.simple_lease_extraction.components.file_lister.local_file_lister import (
    LocalFileLister,
)
from document_extraction_tools.examples.simple_lease_extraction.components.reader.local_file_reader import (
    LocalFileReader,
)
from document_extraction_tools.examples.simple_lease_extraction.config.converter_config import (
    ConverterConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.config.exporter_config import (
    ExporterConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.config.extractor_config import (
    ExtractorConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.config.file_lister_config import (
    FileListerConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.config.reader_config import (
    ReaderConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.runners.orchestrator.orchestrator import (
    PipelineOrchestrator,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the example extraction pipeline."""
    # 1. Load Configuration
    config_path = str(Path(__file__).parent / "config")
    cfg = load_config(
        config_dir=config_path,
        lister_cls=FileListerConfig,
        reader_cls=ReaderConfig,
        converter_cls=ConverterConfig,
        extractor_cls=ExtractorConfig,
        exporter_cls=ExporterConfig,
    )

    logger.info("Configuration loaded successfully.")

    # 2. Instantiate Components using Config
    lister = LocalFileLister(cfg.file_lister)

    orchestrator = PipelineOrchestrator.from_config(
        config=cfg,
        schema=SimpleLeaseDetails,
        reader_cls=LocalFileReader,
        converter_cls=PDFToImageConverter,
        extractor_cls=GeminiImageExtractor,
        exporter_cls=LocalFileExporter,
    )

    # 3. Execute Pipeline
    files = lister.list_files()

    logger.info(f"Found {len(files)} files to process.")

    await orchestrator.run(files)


if __name__ == "__main__":
    asyncio.run(main())
