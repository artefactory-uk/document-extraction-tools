"""Evaluation orchestrator.

This module defines the EvaluationOrchestrator class, which coordinates
the evaluation of extraction models against ground-truth data using multiple
evaluators. It handles loading test examples, reading and converting documents,
running extraction, applying evaluators, and exporting results.
"""

from __future__ import annotations

import asyncio
import contextvars
import logging
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Generic, TypeVar

from document_extraction_tools.base.converter.base_converter import BaseConverter
from document_extraction_tools.base.evaluator.base_evaluator import BaseEvaluator
from document_extraction_tools.base.exporter.base_evaluation_exporter import (
    BaseEvaluationExporter,
)
from document_extraction_tools.base.extractor.base_extractor import BaseExtractor
from document_extraction_tools.base.reader.base_reader import BaseReader
from document_extraction_tools.base.test_data_loader.base_test_data_loader import (
    BaseTestDataLoader,
)
from document_extraction_tools.config.evaluation_orchestrator_config import (
    EvaluationOrchestratorConfig,
)
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.document_bytes import DocumentBytes
from document_extraction_tools.types.evaluation_result import EvaluationResult
from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.schema import ExtractionSchema
from document_extraction_tools.types.test_example import TestExample

logger = logging.getLogger(__name__)
T = TypeVar("T")


class EvaluationOrchestrator(Generic[ExtractionSchema]):
    """Coordinates evaluation across multiple evaluators."""

    def __init__(
        self,
        config: EvaluationOrchestratorConfig,
        test_data_loader: BaseTestDataLoader[ExtractionSchema],
        reader: BaseReader,
        converter: BaseConverter,
        extractor: BaseExtractor,
        evaluators: Iterable[BaseEvaluator[ExtractionSchema]],
        exporter: BaseEvaluationExporter,
        schema: type[ExtractionSchema],
    ) -> None:
        """Initialize the evaluation orchestrator with pipeline components.

        Args:
            config (EvaluationOrchestratorConfig): Configuration for evaluation orchestration.
            test_data_loader (BaseTestDataLoader[ExtractionSchema]): Component to load evaluation examples.
            reader (BaseReader): Component to read raw file bytes.
            converter (BaseConverter): Component to transform bytes into Document objects.
            extractor (BaseExtractor): Component to generate predictions.
            evaluators (Iterable[BaseEvaluator[ExtractionSchema]]): Metrics to apply to each example.
            exporter (BaseEvaluationExporter): Component to persist evaluation results.
            schema (type[ExtractionSchema]): The target Pydantic model definition for extraction.
        """
        self.config = config
        self.test_data_loader = test_data_loader
        self.reader = reader
        self.converter = converter
        self.extractor = extractor
        self.evaluators = list(evaluators)
        self.exporter = exporter
        self.schema = schema

    @classmethod
    def from_config(
        cls,
        config: EvaluationPipelineConfig,
        schema: type[ExtractionSchema],
        reader_cls: type[BaseReader],
        converter_cls: type[BaseConverter],
        extractor_cls: type[BaseExtractor],
        test_data_loader_cls: type[BaseTestDataLoader[ExtractionSchema]],
        evaluator_classes: list[type[BaseEvaluator[ExtractionSchema]]],
        evaluation_exporter_cls: type[BaseEvaluationExporter],
    ) -> EvaluationOrchestrator[ExtractionSchema]:
        """Factory method to create an EvaluationOrchestrator from config.

        Args:
            config (EvaluationPipelineConfig): The full evaluation pipeline configuration.
            schema (type[ExtractionSchema]): The target Pydantic model definition for extraction.
            reader_cls (type[BaseReader]): The concrete Reader class to instantiate.
            converter_cls (type[BaseConverter]): The concrete Converter class to instantiate.
            extractor_cls (type[BaseExtractor]): The concrete Extractor class to instantiate.
            test_data_loader_cls (type[BaseTestDataLoader[ExtractionSchema]]): The
                concrete TestDataLoader class to instantiate.
            evaluator_classes (list[type[BaseEvaluator[ExtractionSchema]]]): The
                evaluator classes available for instantiation.
            evaluation_exporter_cls (type[BaseEvaluationExporter]): The concrete
                EvaluationExporter class to instantiate.

        Returns:
            EvaluationOrchestrator[ExtractionSchema]: The configured orchestrator.
        """
        reader_instance = reader_cls(config.reader)
        converter_instance = converter_cls(config.converter)
        extractor_instance = extractor_cls(config.extractor)
        test_data_loader_instance = test_data_loader_cls(config.test_data_loader)
        evaluation_exporter_instance = evaluation_exporter_cls(
            config.evaluation_exporter
        )

        config_lookup = {
            item.__class__.__name__.replace("Config", ""): item
            for item in config.evaluators
        }

        evaluators = []
        for evaluator_cls in evaluator_classes:
            evaluator_key = evaluator_cls.__name__
            evaluator_config = config_lookup.get(evaluator_key)

            if evaluator_config is not None:
                evaluators.append(evaluator_cls(evaluator_config))
            else:
                raise ValueError(
                    f"No configuration found for evaluator '{evaluator_key}'."
                )
        if not evaluators:
            raise ValueError("No valid evaluators configured.")

        return cls(
            config=config.orchestrator,
            test_data_loader=test_data_loader_instance,
            reader=reader_instance,
            converter=converter_instance,
            extractor=extractor_instance,
            evaluators=evaluators,
            exporter=evaluation_exporter_instance,
            schema=schema,
        )

    @staticmethod
    def _ingest(
        path_identifier: PathIdentifier,
        reader: BaseReader,
        converter: BaseConverter,
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

    async def process_example(
        self,
        example: TestExample[ExtractionSchema],
        pool: ThreadPoolExecutor,
        semaphore: asyncio.Semaphore,
    ) -> tuple[Document, list[EvaluationResult]]:
        """Runs extraction, evaluation, and export for a single example.

        Args:
            example (TestExample[ExtractionSchema]): The test example to process.
            pool (ThreadPoolExecutor): The thread pool for CPU-bound tasks.
            semaphore (asyncio.Semaphore): Semaphore to limit concurrency.

        Returns:
            tuple[Document, list[EvaluationResult]]: The document and its evaluation results.
        """
        loop = asyncio.get_running_loop()

        document: Document = await self._run_in_executor_with_context(
            loop,
            pool,
            self._ingest,
            example.path_identifier,
            self.reader,
            self.converter,
        )

        async with semaphore:
            pred: ExtractionSchema = await self.extractor.extract(document, self.schema)

            evaluation_tasks = [
                self._run_in_executor_with_context(
                    loop, pool, evaluator.evaluate, example.true, pred
                )
                for evaluator in self.evaluators
            ]
            results: list[EvaluationResult] = list(
                await asyncio.gather(*evaluation_tasks)
            )

            logger.info("Completed evaluation for %s", document.id)
            return document, results

    async def run(
        self,
        examples: list[TestExample[ExtractionSchema]],
    ) -> None:
        """Run all evaluators and export results for the provided examples.

        Args:
            examples (list[TestExample[ExtractionSchema]]): The test examples to evaluate.
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrency)

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as pool:
            tasks = [
                self.process_example(example, pool, semaphore) for example in examples
            ]

            results_or_exceptions = await asyncio.gather(*tasks, return_exceptions=True)

            valid_results: list[tuple[Document, list[EvaluationResult]]] = []

            for example, result in zip(examples, results_or_exceptions, strict=True):
                if isinstance(result, BaseException):
                    logger.error(
                        "Evaluation pipeline failed for %s",
                        example.path_identifier,
                        exc_info=result,
                    )
                else:
                    valid_results.append(result)

            if valid_results:
                await self.exporter.export(valid_results)
