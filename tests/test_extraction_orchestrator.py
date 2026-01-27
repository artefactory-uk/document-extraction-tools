"""Tests for the extraction orchestrator."""

from __future__ import annotations

import asyncio
import contextvars
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import BaseModel

from document_extraction_tools.base import (
    BaseConverter,
    BaseExtractionExporter,
    BaseExtractor,
    BaseReader,
)
from document_extraction_tools.config import (
    BaseConverterConfig,
    BaseExtractionExporterConfig,
    BaseExtractorConfig,
    BaseFileListerConfig,
    BaseReaderConfig,
    ExtractionOrchestratorConfig,
    ExtractionPipelineConfig,
)
from document_extraction_tools.runners import (
    ExtractionOrchestrator,
)
from document_extraction_tools.types import (
    Document,
    DocumentBytes,
    Page,
    PathIdentifier,
    TextData,
)


class DummySchema(BaseModel):
    """Minimal schema for extraction tests."""

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
            pages=[
                Page(page_number=1, data=TextData(content="hello")),
            ],
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
        return schema(value=f"extracted:{document.id}")


class DummyExporter(BaseExtractionExporter):
    """Exporter stub that records calls."""

    def __init__(self, config: BaseExtractionExporterConfig) -> None:
        """Initialize the exporter stub."""
        super().__init__(config)
        self.export_calls: list[tuple[Document, DummySchema]] = []

    async def export(self, document: Document, data: DummySchema) -> None:
        """Record exports without persisting data."""
        self.export_calls.append((document, data))


def test_from_config_wires_components() -> None:
    """Instantiate and wire pipeline components from config."""
    config = ExtractionPipelineConfig(
        orchestrator=ExtractionOrchestratorConfig(max_workers=1, max_concurrency=2),
        file_lister=BaseFileListerConfig(),
        reader=BaseReaderConfig(),
        converter=BaseConverterConfig(),
        extractor=BaseExtractorConfig(),
        exporter=BaseExtractionExporterConfig(),
    )

    orchestrator = ExtractionOrchestrator.from_config(
        config=config,
        schema=DummySchema,
        reader_cls=DummyReader,
        converter_cls=DummyConverter,
        extractor_cls=DummyExtractor,
        exporter_cls=DummyExporter,
    )

    assert isinstance(orchestrator.reader, DummyReader)
    assert isinstance(orchestrator.converter, DummyConverter)
    assert isinstance(orchestrator.extractor, DummyExtractor)
    assert isinstance(orchestrator.exporter, DummyExporter)
    assert orchestrator.config.max_workers == 1
    assert orchestrator.schema is DummySchema


@pytest.mark.asyncio
async def test_run_in_executor_with_context_preserves_contextvars() -> None:
    """Keep contextvars values when running in the executor."""
    token = contextvars.ContextVar("token", default="missing")
    token.set("present")

    def read_token() -> str:
        return token.get()

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = await ExtractionOrchestrator._run_in_executor_with_context(
            loop, pool, read_token
        )

    assert result == "present"


@pytest.mark.asyncio
async def test_process_document_runs_pipeline() -> None:
    """Run the full pipeline for a single document."""
    reader = DummyReader(BaseReaderConfig())
    converter = DummyConverter(BaseConverterConfig())
    extractor = DummyExtractor(BaseExtractorConfig())
    exporter = DummyExporter(BaseExtractionExporterConfig())
    orchestrator = ExtractionOrchestrator(
        config=ExtractionOrchestratorConfig(max_workers=1, max_concurrency=1),
        reader=reader,
        converter=converter,
        extractor=extractor,
        exporter=exporter,
        schema=DummySchema,
    )

    path = PathIdentifier(path="doc-1")
    with ThreadPoolExecutor(max_workers=1) as pool:
        await orchestrator.process_document(path, pool, asyncio.Semaphore(1))

    assert reader.read_calls == [path]
    assert len(converter.convert_calls) == 1
    assert len(extractor.extract_calls) == 1
    assert len(exporter.export_calls) == 1
    assert exporter.export_calls[0][1].value == "extracted:doc-1"


@pytest.mark.asyncio
async def test_run_skips_failed_documents() -> None:
    """Skip exports when a document fails during processing."""
    reader = DummyReader(BaseReaderConfig())
    converter = DummyConverter(BaseConverterConfig())
    extractor = DummyExtractor(BaseExtractorConfig(), fail_on="doc-fail")
    exporter = DummyExporter(BaseExtractionExporterConfig())
    orchestrator = ExtractionOrchestrator(
        config=ExtractionOrchestratorConfig(max_workers=2, max_concurrency=2),
        reader=reader,
        converter=converter,
        extractor=extractor,
        exporter=exporter,
        schema=DummySchema,
    )

    await orchestrator.run(
        [PathIdentifier(path="doc-ok"), PathIdentifier(path="doc-fail")]
    )

    exported_ids = {doc.id for doc, _ in exporter.export_calls}
    assert exported_ids == {"doc-ok"}
