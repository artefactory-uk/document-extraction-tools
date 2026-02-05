"""Extraction Orchestrator.

This module contains the logic to coordinate the flow of data through the
extraction pipeline. It manages parallel processing and asynchronous
concurrency to maximize throughput.
"""

import asyncio
import contextvars
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Generic, TypeVar

from document_extraction_tools.base.converter.base_converter import BaseConverter
from document_extraction_tools.base.exporter.base_extraction_exporter import (
    BaseExtractionExporter,
)
from document_extraction_tools.base.extractor.base_extractor import BaseExtractor
from document_extraction_tools.base.reader.base_reader import BaseReader
from document_extraction_tools.config.extraction_orchestrator_config import (
    ExtractionOrchestratorConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.document_bytes import DocumentBytes
from document_extraction_tools.types.extraction_result import (
    ExtractionResult,
    ExtractionSchema,
)
from document_extraction_tools.types.path_identifier import PathIdentifier

logger = logging.getLogger(__name__)
T = TypeVar("T")


class ExtractionOrchestrator(Generic[ExtractionSchema]):
    """Coordinates the document extraction pipeline.

    This class manages the lifecycle of document processing, ensuring that
    CPU-bound tasks (Reading/Converting) are offloaded to a thread pool while
    I/O-bound tasks (Extracting/Exporting) run concurrently in the async event
    loop.

    Attributes:
        config (ExtractionOrchestratorConfig): Orchestrator configuration.
        reader (BaseReader): Reader component instance.
        converter (BaseConverter): Converter component instance.
        extractor (BaseExtractor): Extractor component instance.
        exporter (BaseExtractionExporter): Exporter component instance.
        schema (type[ExtractionSchema]): Target extraction schema.
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
        reader_instance = reader_cls(config)
        converter_instance = converter_cls(config)
        extractor_instance = extractor_cls(config)
        exporter_instance = exporter_cls(config)

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
        path_identifier: PathIdentifier,
        reader: BaseReader,
        converter: BaseConverter,
        context: PipelineContext,
    ) -> Document:
        """Performs the CPU-bound ingestion phase.

        Args:
            path_identifier (PathIdentifier): The path identifier to the source file.
            reader (BaseReader): The reader instance to use.
            converter (BaseConverter): The converter instance to use.
            context (PipelineContext): Shared pipeline context.

        Returns:
            Document: The fully parsed document object.
        """
        doc_bytes: DocumentBytes = reader.read(path_identifier, context)
        return converter.convert(doc_bytes, context)

    @staticmethod
    async def _run_in_executor_with_context(
        loop: asyncio.AbstractEventLoop,
        pool: ThreadPoolExecutor,
        func: Callable[..., T],
        *args: object,
    ) -> T:
        """Run a function in an executor while preserving contextvars.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop to use.
            pool (ThreadPoolExecutor): The thread pool to run the function in.
            func (Callable[..., T]): The function to execute.
            *args (object): Arguments to pass to the function.

        Returns:
            The result of the function execution.
        """
        ctx = contextvars.copy_context()
        return await loop.run_in_executor(pool, ctx.run, func, *args)

    async def process_document(
        self,
        path_identifier: PathIdentifier,
        pool: ThreadPoolExecutor,
        semaphore: asyncio.Semaphore,
        context: PipelineContext,
    ) -> None:
        """Runs the full processing lifecycle for a single document.

        1. Ingest (Read+Convert) -> Offloaded to ThreadPool (CPU).
        2. Extract -> Async Wait (I/O).
        3. Export -> Async Wait (I/O).

        Args:
            path_identifier (PathIdentifier): The input file to process.
            pool (ThreadPoolExecutor): The shared pool for CPU tasks.
            semaphore (asyncio.Semaphore): The shared limiter for I/O tasks.
            context (PipelineContext): Shared pipeline context.
        """
        loop = asyncio.get_running_loop()

        document: Document = await self._run_in_executor_with_context(
            loop,
            pool,
            self._ingest,
            path_identifier,
            self.reader,
            self.converter,
            context,
        )

        async with semaphore:
            extracted_data: ExtractionResult[ExtractionSchema] = (
                await self.extractor.extract(document, self.schema, context)
            )
            await self.exporter.export(document, extracted_data, context)

            logger.info("Completed extraction for %s", document.id)

    async def run(
        self,
        file_paths_to_process: list[PathIdentifier],
        context: PipelineContext | None = None,
    ) -> None:
        """Main entry point. Orchestrates the execution of the provided file list.

        Args:
            file_paths_to_process (list[PathIdentifier]): The list of file paths to process.
            context (PipelineContext | None): Optional shared pipeline context.
        """
        context = context or PipelineContext()
        semaphore = asyncio.Semaphore(self.config.max_concurrency)

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as pool:

            tasks = [
                self.process_document(path_identifier, pool, semaphore, context)
                for path_identifier in file_paths_to_process
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for path_identifier, result in zip(
                file_paths_to_process, results, strict=True
            ):
                if isinstance(result, BaseException):
                    logger.error(
                        "Extraction pipeline failed for %s",
                        path_identifier,
                        exc_info=result,
                    )
