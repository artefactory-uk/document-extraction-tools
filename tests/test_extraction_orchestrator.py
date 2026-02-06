"""Tests for the extraction orchestrator."""

import asyncio
import contextvars
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import BaseModel

from document_extraction_tools.base import (
    BaseConverter,
    BaseExtractionExporter,
    BaseExtractor,
    BaseFileLister,
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
    ExtractionResult,
    Page,
    PathIdentifier,
    PipelineContext,
    TextData,
)


class DummySchema(BaseModel):
    """Minimal schema for extraction tests."""

    value: str


class DummyFileLister(BaseFileLister):
    """File lister stub used for wiring tests."""

    def __init__(
        self,
        config: BaseFileListerConfig | ExtractionPipelineConfig,
    ) -> None:
        """Initialize the file lister stub."""
        super().__init__(config)

    def list_files(
        self, _context: PipelineContext | None = None
    ) -> list[PathIdentifier]:
        """Return an empty list for tests."""
        return []


class DummyReader(BaseReader):
    """Reader stub that records calls."""

    def __init__(self, config: BaseReaderConfig | ExtractionPipelineConfig) -> None:
        """Initialize the reader stub."""
        super().__init__(config)
        self.read_calls: list[PathIdentifier] = []

    def read(
        self, path_identifier: PathIdentifier, _context: PipelineContext | None = None
    ) -> DocumentBytes:
        """Return fixed bytes while tracking read calls."""
        self.read_calls.append(path_identifier)
        return DocumentBytes(
            file_bytes=b"data",
            path_identifier=path_identifier,
        )


class DummyConverter(BaseConverter):
    """Converter stub that records calls."""

    def __init__(self, config: BaseConverterConfig | ExtractionPipelineConfig) -> None:
        """Initialize the converter stub."""
        super().__init__(config)
        self.convert_calls: list[DocumentBytes] = []

    def convert(
        self, document_bytes: DocumentBytes, _context: PipelineContext | None = None
    ) -> Document:
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

    def __init__(
        self,
        config: BaseExtractorConfig | ExtractionPipelineConfig,
        fail_on: str | None = None,
    ) -> None:
        """Initialize the extractor stub with an optional failure id."""
        super().__init__(config)
        self.fail_on = fail_on
        self.extract_calls: list[Document] = []

    async def extract(
        self,
        document: Document,
        schema: type[DummySchema],
        _context: PipelineContext | None = None,
    ) -> ExtractionResult[DummySchema]:
        """Return a schema instance or raise for configured ids."""
        self.extract_calls.append(document)
        if self.fail_on is not None and document.id == self.fail_on:
            raise RuntimeError("boom")
        return ExtractionResult(data=schema(value=f"extracted:{document.id}"))


class DummyExporter(BaseExtractionExporter):
    """Exporter stub that records calls."""

    def __init__(
        self,
        config: BaseExtractionExporterConfig | ExtractionPipelineConfig,
    ) -> None:
        """Initialize the exporter stub."""
        super().__init__(config)
        self.export_calls: list[tuple[Document, DummySchema]] = []

    async def export(
        self,
        document: Document,
        data: ExtractionResult[DummySchema],
        _context: PipelineContext | None = None,
    ) -> None:
        """Record exports without persisting data."""
        self.export_calls.append((document, data))


def test_from_config_wires_components() -> None:
    """Instantiate and wire pipeline components from config."""
    config = ExtractionPipelineConfig(
        extraction_orchestrator=ExtractionOrchestratorConfig(),
        file_lister=BaseFileListerConfig(),
        reader=BaseReaderConfig(),
        converter=BaseConverterConfig(),
        extractor=BaseExtractorConfig(),
        extraction_exporter=BaseExtractionExporterConfig(),
    )

    orchestrator = ExtractionOrchestrator.from_config(
        config=config,
        schema=DummySchema,
        file_lister_cls=DummyFileLister,
        reader_cls=DummyReader,
        converter_cls=DummyConverter,
        extractor_cls=DummyExtractor,
        extraction_exporter_cls=DummyExporter,
    )

    assert isinstance(orchestrator.file_lister, DummyFileLister)
    assert isinstance(orchestrator.reader, DummyReader)
    assert isinstance(orchestrator.converter, DummyConverter)
    assert isinstance(orchestrator.extractor, DummyExtractor)
    assert isinstance(orchestrator.extraction_exporter, DummyExporter)
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
    pipeline_config = ExtractionPipelineConfig(
        extraction_orchestrator=ExtractionOrchestratorConfig(),
        file_lister=BaseFileListerConfig(),
        reader=BaseReaderConfig(),
        converter=BaseConverterConfig(),
        extractor=BaseExtractorConfig(),
        extraction_exporter=BaseExtractionExporterConfig(),
    )
    reader = DummyReader(pipeline_config)
    converter = DummyConverter(pipeline_config)
    extractor = DummyExtractor(pipeline_config)
    exporter = DummyExporter(pipeline_config)
    orchestrator = ExtractionOrchestrator(
        config=pipeline_config.extraction_orchestrator,
        file_lister=DummyFileLister(pipeline_config),
        reader=reader,
        converter=converter,
        extractor=extractor,
        extraction_exporter=exporter,
        schema=DummySchema,
    )

    path = PathIdentifier(path="doc-1")
    with ThreadPoolExecutor(max_workers=1) as pool:
        await orchestrator.process_document(
            path, pool, asyncio.Semaphore(1), PipelineContext()
        )

    assert reader.read_calls == [path]
    assert len(converter.convert_calls) == 1
    assert len(extractor.extract_calls) == 1
    assert len(exporter.export_calls) == 1
    assert exporter.export_calls[0][1].data.value == "extracted:doc-1"


@pytest.mark.asyncio
async def test_run_skips_failed_documents() -> None:
    """Skip exports when a document fails during processing."""
    pipeline_config = ExtractionPipelineConfig(
        extraction_orchestrator=ExtractionOrchestratorConfig(),
        file_lister=BaseFileListerConfig(),
        reader=BaseReaderConfig(),
        converter=BaseConverterConfig(),
        extractor=BaseExtractorConfig(),
        extraction_exporter=BaseExtractionExporterConfig(),
    )
    reader = DummyReader(pipeline_config)
    converter = DummyConverter(pipeline_config)
    extractor = DummyExtractor(pipeline_config, fail_on="doc-fail")
    exporter = DummyExporter(pipeline_config)
    orchestrator = ExtractionOrchestrator(
        config=pipeline_config.extraction_orchestrator,
        file_lister=DummyFileLister(pipeline_config),
        reader=reader,
        converter=converter,
        extractor=extractor,
        extraction_exporter=exporter,
        schema=DummySchema,
    )

    await orchestrator.run(
        [PathIdentifier(path="doc-ok"), PathIdentifier(path="doc-fail")]
    )

    exported_ids = {doc.id for doc, _ in exporter.export_calls}
    assert exported_ids == {"doc-ok"}
