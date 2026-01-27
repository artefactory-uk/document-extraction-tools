"""Tests for the evaluation orchestrator."""

from __future__ import annotations

import asyncio
import contextvars
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import BaseModel

from document_extraction_tools.base import (
    BaseConverter,
    BaseEvaluationExporter,
    BaseEvaluator,
    BaseExtractor,
    BaseReader,
    BaseTestDataLoader,
)
from document_extraction_tools.config import (
    BaseConverterConfig,
    BaseEvaluationExporterConfig,
    BaseEvaluatorConfig,
    BaseExtractorConfig,
    BaseReaderConfig,
    BaseTestDataLoaderConfig,
    EvaluationOrchestratorConfig,
    EvaluationPipelineConfig,
)
from document_extraction_tools.runners import (
    EvaluationOrchestrator,
)
from document_extraction_tools.types import (
    Document,
    DocumentBytes,
    EvaluationResult,
    Page,
    PathIdentifier,
    TestExample,
    TextData,
)


class DummySchema(BaseModel):
    """Minimal schema for evaluation tests."""

    value: str


class DummyReader(BaseReader):
    """Reader stub that records calls."""

    def __init__(self, config: BaseReaderConfig) -> None:
        """Initialize the reader stub."""
        super().__init__(config)
        self.read_calls: list[PathIdentifier] = []

    def read(self, path_identifier: PathIdentifier) -> DocumentBytes:
        """Return fixed bytes while tracking read calls."""
        self.read_calls.append(path_identifier)
        return DocumentBytes(
            file_bytes=b"data",
            path_identifier=path_identifier,
            mime_type="text/plain",
        )


class DummyConverter(BaseConverter):
    """Converter stub that records calls."""

    def __init__(self, config: BaseConverterConfig) -> None:
        """Initialize the converter stub."""
        super().__init__(config)
        self.convert_calls: list[DocumentBytes] = []

    def convert(self, document_bytes: DocumentBytes) -> Document:
        """Return a minimal document while tracking conversion calls."""
        self.convert_calls.append(document_bytes)
        return Document(
            id=str(document_bytes.path_identifier.path),
            content_type="text",
            pages=[Page(page_number=1, data=TextData(content="hello"))],
            path_identifier=document_bytes.path_identifier,
            metadata={},
        )


class DummyExtractor(BaseExtractor):
    """Extractor stub that can be configured to fail."""

    def __init__(self, config: BaseExtractorConfig, fail_on: str | None = None) -> None:
        """Initialize the extractor stub with an optional failure id."""
        super().__init__(config)
        self.fail_on = fail_on
        self.extract_calls: list[Document] = []

    async def extract(
        self, document: Document, schema: type[DummySchema]
    ) -> DummySchema:
        """Return a schema instance or raise for configured ids."""
        self.extract_calls.append(document)
        if self.fail_on is not None and document.id == self.fail_on:
            raise RuntimeError("boom")
        return schema(value=f"pred:{document.id}")


class DummyEvaluatorConfig(BaseEvaluatorConfig):
    """Config placeholder for evaluator tests."""

    pass


class DummyEvaluator(BaseEvaluator[DummySchema]):
    """Evaluator stub that records calls."""

    def __init__(self, config: DummyEvaluatorConfig) -> None:
        """Initialize the evaluator stub."""
        super().__init__(config)
        self.evaluate_calls: list[tuple[DummySchema, DummySchema]] = []

    def evaluate(self, true: DummySchema, pred: DummySchema) -> EvaluationResult:
        """Return a dummy evaluation result while tracking calls."""
        self.evaluate_calls.append((true, pred))
        return EvaluationResult(
            name="dummy",
            result=true.value == pred.value,
            description="Equality check",
        )


class DummyTestDataLoader(BaseTestDataLoader[DummySchema]):
    """Test data loader stub for wiring tests."""

    def load_test_data(
        self, _path_identifier: PathIdentifier
    ) -> list[TestExample[DummySchema]]:
        """Return an empty set of examples for tests."""
        return []


class DummyEvaluationExporter(BaseEvaluationExporter):
    """Evaluation exporter stub that records calls."""

    def __init__(self, config: BaseEvaluationExporterConfig) -> None:
        """Initialize the exporter stub."""
        super().__init__(config)
        self.export_calls: list[list[tuple[Document, list[EvaluationResult]]]] = []

    async def export(
        self, results: list[tuple[Document, list[EvaluationResult]]]
    ) -> None:
        """Record evaluation results without persisting data."""
        self.export_calls.append(results)


def test_from_config_wires_components_and_evaluators() -> None:
    """Instantiate and wire evaluation components from config."""
    config = EvaluationPipelineConfig(
        orchestrator=EvaluationOrchestratorConfig(max_workers=1, max_concurrency=2),
        test_data_loader=BaseTestDataLoaderConfig(),
        evaluators=[DummyEvaluatorConfig()],
        reader=BaseReaderConfig(),
        converter=BaseConverterConfig(),
        extractor=BaseExtractorConfig(),
        evaluation_exporter=BaseEvaluationExporterConfig(),
    )

    orchestrator = EvaluationOrchestrator.from_config(
        config=config,
        schema=DummySchema,
        reader_cls=DummyReader,
        converter_cls=DummyConverter,
        extractor_cls=DummyExtractor,
        test_data_loader_cls=DummyTestDataLoader,
        evaluator_classes=[DummyEvaluator],
        evaluation_exporter_cls=DummyEvaluationExporter,
    )

    assert isinstance(orchestrator.reader, DummyReader)
    assert isinstance(orchestrator.converter, DummyConverter)
    assert isinstance(orchestrator.extractor, DummyExtractor)
    assert isinstance(orchestrator.test_data_loader, DummyTestDataLoader)
    assert isinstance(orchestrator.exporter, DummyEvaluationExporter)
    assert len(orchestrator.evaluators) == 1
    assert isinstance(orchestrator.evaluators[0], DummyEvaluator)


@pytest.mark.asyncio
async def test_run_in_executor_with_context_preserves_contextvars() -> None:
    """Keep contextvars values when running in the executor."""
    token = contextvars.ContextVar("token", default="missing")
    token.set("present")

    def read_token() -> str:
        return token.get()

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = await EvaluationOrchestrator._run_in_executor_with_context(
            loop, pool, read_token
        )

    assert result == "present"


def test_from_config_missing_evaluator_config_raises() -> None:
    """Raise when evaluator config is missing for an evaluator class."""
    config = EvaluationPipelineConfig(
        orchestrator=EvaluationOrchestratorConfig(max_workers=1, max_concurrency=2),
        test_data_loader=BaseTestDataLoaderConfig(),
        evaluators=[],
        reader=BaseReaderConfig(),
        converter=BaseConverterConfig(),
        extractor=BaseExtractorConfig(),
        evaluation_exporter=BaseEvaluationExporterConfig(),
    )

    with pytest.raises(ValueError, match="No configuration found for evaluator"):
        EvaluationOrchestrator.from_config(
            config=config,
            schema=DummySchema,
            reader_cls=DummyReader,
            converter_cls=DummyConverter,
            extractor_cls=DummyExtractor,
            test_data_loader_cls=DummyTestDataLoader,
            evaluator_classes=[DummyEvaluator],
            evaluation_exporter_cls=DummyEvaluationExporter,
        )


@pytest.mark.asyncio
async def test_process_example_runs_pipeline() -> None:
    """Run extraction and evaluation for one example."""
    orchestrator = EvaluationOrchestrator(
        config=EvaluationOrchestratorConfig(max_workers=1, max_concurrency=1),
        test_data_loader=DummyTestDataLoader(BaseTestDataLoaderConfig()),
        reader=DummyReader(BaseReaderConfig()),
        converter=DummyConverter(BaseConverterConfig()),
        extractor=DummyExtractor(BaseExtractorConfig()),
        evaluators=[DummyEvaluator(DummyEvaluatorConfig())],
        exporter=DummyEvaluationExporter(BaseEvaluationExporterConfig()),
        schema=DummySchema,
    )

    example: TestExample[DummySchema] = TestExample(
        id="example-1",
        path_identifier=PathIdentifier(path="doc-1"),
        true=DummySchema(value="pred:doc-1"),
    )

    with ThreadPoolExecutor(max_workers=1) as pool:
        document, results = await orchestrator.process_example(
            example, pool, asyncio.Semaphore(1)
        )

    assert document.id == "doc-1"
    assert len(results) == 1
    assert results[0].name == "dummy"


@pytest.mark.asyncio
async def test_run_exports_only_valid_results() -> None:
    """Export only successful example results."""
    exporter = DummyEvaluationExporter(BaseEvaluationExporterConfig())
    orchestrator = EvaluationOrchestrator(
        config=EvaluationOrchestratorConfig(max_workers=2, max_concurrency=2),
        test_data_loader=DummyTestDataLoader(BaseTestDataLoaderConfig()),
        reader=DummyReader(BaseReaderConfig()),
        converter=DummyConverter(BaseConverterConfig()),
        extractor=DummyExtractor(BaseExtractorConfig(), fail_on="doc-fail"),
        evaluators=[DummyEvaluator(DummyEvaluatorConfig())],
        exporter=exporter,
        schema=DummySchema,
    )

    examples: list[TestExample[DummySchema]] = [
        TestExample(
            id="example-ok",
            path_identifier=PathIdentifier(path="doc-ok"),
            true=DummySchema(value="pred:doc-ok"),
        ),
        TestExample(
            id="example-fail",
            path_identifier=PathIdentifier(path="doc-fail"),
            true=DummySchema(value="pred:doc-fail"),
        ),
    ]

    await orchestrator.run(examples)

    assert len(exporter.export_calls) == 1
    exported_docs = [doc.id for doc, _ in exporter.export_calls[0]]
    assert exported_docs == ["doc-ok"]
