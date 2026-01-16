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
from document_extraction_tools.base.exporter.exporter import BaseExporter
from document_extraction_tools.base.extractor.extractor import BaseExtractor
from document_extraction_tools.base.reader.reader import BaseReader
from document_extraction_tools.schemas.schema import ExtractionSchema
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.path_identifier import PathIdentifier

logger = logging.getLogger(__name__)


class PipelineOrchestrator(Generic[ExtractionSchema]):
    """Coordinates the document extraction pipeline.

    This class manages the lifecycle of document processing, ensuring that
    CPU-bound tasks (Reading/Converting) are offloaded to separate processes
    while I/O-bound tasks (Extracting/Exporting) run concurrently in the
    async event loop.
    """

    def __init__(
        self,
        reader: BaseReader,
        converter: BaseConverter,
        extractor: BaseExtractor,
        exporter: BaseExporter,
        schema: type[ExtractionSchema],
        max_workers: int = 4,
        max_concurrency: int = 10,
    ) -> None:
        """Initialize the orchestrator with pipeline components.

        Args:
            reader (BaseReader): Component to read raw file bytes.
            converter (BaseConverter): Component to transform bytes into Document objects.
            extractor (BaseExtractor): Component to extract structured data via LLM.
            exporter (BaseExporter): Component to persist the results.
            schema (type[ExtractionSchema]): The target Pydantic model definition for extraction.
            max_workers (int): Number of CPU processes for parallel conversion. Defaults to 4.
            max_concurrency (int): Max number of concurrent I/O operations. Defaults to 10.
        """
        self.reader = reader
        self.converter = converter
        self.extractor = extractor
        self.exporter = exporter
        self.schema = schema

        self.max_workers = max_workers
        self.max_concurrency = max_concurrency

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
        doc_bytes = reader.read(path_identifier)
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

        document = await loop.run_in_executor(
            pool, self._ingest, path_identifier, self.reader, self.converter
        )

        async with semaphore:
            extracted_data: ExtractionSchema = await self.extractor.extract(
                document, self.schema
            )
            await self.exporter.export(extracted_data)

    async def run(self, file_paths_to_process: list[PathIdentifier]) -> None:
        """Main entry point. Orchestrates the execution of the provided file list.

        Args:
            file_paths_to_process (list[PathIdentifier]): The list of file paths to process.
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)

        with ProcessPoolExecutor(max_workers=self.max_workers) as pool:

            tasks = [
                self.process_document(path_identifier, pool, semaphore)
                for path_identifier in file_paths_to_process
            ]

            await asyncio.gather(*tasks)
