"""Pipeline Orchestrator.

This module contains the logic to coordinate the flow of data through the
extraction pipeline. It manages parallel processing and asynchronous
concurrency to maximize throughput.
"""

import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Generic

from document_extraction_tools.base.converter.converter import BaseConverter
from document_extraction_tools.base.exporter.extraction_exporter import (
    BaseExtractionExporter,
)
from document_extraction_tools.base.extractor.extractor import BaseExtractor
from document_extraction_tools.base.reader.reader import BaseReader
from document_extraction_tools.config.extraction_orchestrator_config import (
    ExtractionOrchestratorConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.document_bytes import DocumentBytes
from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.schema import ExtractionSchema

logger = logging.getLogger(__name__)


class ExtractionOrchestrator(Generic[ExtractionSchema]):
    """Coordinates the document extraction pipeline.

    This class manages the lifecycle of document processing, ensuring that
    CPU-bound tasks (Reading/Converting) are offloaded to separate processes
    while I/O-bound tasks (Extracting/Exporting) run concurrently in the
    async event loop.
    """

    def __init__(
        self,
        config: ExtractionOrchestratorConfig,
        reader: BaseReader,
        converter: BaseConverter,
        extractor: BaseExtractor,
        exporter: BaseExtractionExporter,
        schema: type[ExtractionSchema],
    ) -> None:
        """Initialize the orchestrator with pipeline components.

        Args:
            config (ExtractionOrchestratorConfig): Configuration for the orchestrator.
            reader (BaseReader): Component to read raw file bytes.
            converter (BaseConverter): Component to transform bytes into Document objects.
            extractor (BaseExtractor): Component to extract structured data via LLM.
            exporter (BaseExtractionExporter): Component to persist the results.
            schema (type[ExtractionSchema]): The target Pydantic model definition for extraction.
        """
        self.config = config
        self.reader = reader
        self.converter = converter
        self.extractor = extractor
        self.exporter = exporter
        self.schema = schema

    @classmethod
    def from_config(
        cls,
        config: ExtractionPipelineConfig,
        schema: type[ExtractionSchema],
        reader_cls: type[BaseReader],
        converter_cls: type[BaseConverter],
        extractor_cls: type[BaseExtractor],
        exporter_cls: type[BaseExtractionExporter],
    ) -> "ExtractionOrchestrator[ExtractionSchema]":
        """Factory method to create an Orchestrator from a PipelineConfig.

        Args:
            config (ExtractionPipelineConfig): The full pipeline configuration.
            schema (type[ExtractionSchema]): The target Pydantic model definition for extraction.
            reader_cls (type[BaseReader]): The concrete Reader class to instantiate.
            converter_cls (type[BaseConverter]): The concrete Converter class to instantiate.
            extractor_cls (type[BaseExtractor]): The concrete Extractor class to instantiate.
            exporter_cls (type[BaseExtractionExporter]): The concrete Exporter class to instantiate.

        Returns:
            ExtractionOrchestrator[ExtractionSchema]: The configured orchestrator instance.
        """
        reader_instance = reader_cls(config.reader)
        converter_instance = converter_cls(config.converter)
        extractor_instance = extractor_cls(config.extractor)
        exporter_instance = exporter_cls(config.exporter)

        return cls(
            config=config.orchestrator,
            reader=reader_instance,
            converter=converter_instance,
            extractor=extractor_instance,
            exporter=exporter_instance,
            schema=schema,
        )

    @staticmethod
    def _ingest(
        path_identifier: PathIdentifier, reader: BaseReader, converter: BaseConverter
    ) -> Document:
        """Performs the CPU-bound ingestion phase.

        Args:
            path_identifier (PathIdentifier): The path identifier to the source file.
            reader (BaseReader): The reader instance to use.
            converter (BaseConverter): The converter instance to use.

        Returns:
            Document: The fully parsed document object.
        """
        doc_bytes: DocumentBytes = reader.read(path_identifier)
        return converter.convert(doc_bytes)

    async def process_document(
        self,
        path_identifier: PathIdentifier,
        pool: ProcessPoolExecutor,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """Runs the full processing lifecycle for a single document.

        1. Ingest (Read+Convert) -> Offloaded to ProcessPool (CPU).
        2. Extract -> Async Wait (I/O).
        3. Export -> Async Wait (I/O).

        Args:
            path_identifier (PathIdentifier): The input file to process.
            pool (ProcessPoolExecutor): The shared pool for CPU tasks.
            semaphore (asyncio.Semaphore): The shared limiter for I/O tasks.
        """
        loop = asyncio.get_running_loop()

        document: Document = await loop.run_in_executor(
            pool, self._ingest, path_identifier, self.reader, self.converter
        )

        async with semaphore:
            extracted_data: ExtractionSchema = await self.extractor.extract(
                document, self.schema
            )
            await self.exporter.export(document, extracted_data)

    async def run(self, file_paths_to_process: list[PathIdentifier]) -> None:
        """Main entry point. Orchestrates the execution of the provided file list.

        Args:
            file_paths_to_process (list[PathIdentifier]): The list of file paths to process.
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrency)

        with ProcessPoolExecutor(max_workers=self.config.max_workers) as pool:

            tasks = [
                self.process_document(path_identifier, pool, semaphore)
                for path_identifier in file_paths_to_process
            ]

            await asyncio.gather(*tasks)
