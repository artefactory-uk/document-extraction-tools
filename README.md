# document-extraction-tools

A modular, high-performance toolkit for building document extraction pipelines. The library provides clear interfaces for every pipeline stage, plus orchestrators that wire the stages together with async I/O and CPU-bound parallelism.

This repo is intentionally implementation-light: you plug in your own components (readers, converters, extractors, exporters, evaluators) for each specific document type or data source.

## What this library gives you

- A consistent set of **interfaces** for the entire document-extraction lifecycle.
- A **typed data model** for documents, pages, and extraction results.
- **Orchestrators** that run extraction and evaluation pipelines concurrently and safely.
- A **configuration system** (Pydantic + YAML) for repeatable pipelines.

## Core concepts and components

### Extraction pipeline

1. **FileLister** (`BaseFileLister`)
   - Discovers input files and returns a list of `PathIdentifier` objects.

2. **Reader** (`BaseReader`)
   - Reads raw bytes from the source and returns `DocumentBytes`.

3. **Converter** (`BaseConverter`)
   - Converts raw bytes into a structured `Document` (pages, metadata, content type).

4. **Extractor** (`BaseExtractor`)
   - Asynchronously extracts structured data into a Pydantic schema (`ExtractionSchema`).

5. **ExtractionExporter** (`BaseExtractionExporter`)
   - Asynchronously persists extracted data to your desired destination (DB, files, API, etc.).

6. **ExtractionOrchestrator**
   - Runs the pipeline with a thread pool for CPU-bound steps (read/convert) and async
     concurrency for I/O-bound steps (extract/export).

### Evaluation pipeline

1. **TestDataLoader** (`BaseTestDataLoader`)
   - Loads evaluation examples (ground truth + file path) as `EvaluationExample`.

2. **Evaluator** (`BaseEvaluator`)
   - Computes a metric by comparing `true` vs. `pred` schemas.

3. **EvaluationExporter** (`BaseEvaluationExporter`)
   - Persists evaluation results.

4. **EvaluationOrchestrator**
   - Runs extraction + evaluation across examples with the same concurrency model
     (thread pool + async I/O).

### Data models

- `PathIdentifier`: A uniform handle for file locations plus optional context.
- `DocumentBytes`: Raw bytes + MIME type + path identifier.
- `Document`: Parsed content (pages, text/image data, metadata).
- `ExtractionSchema`: Your Pydantic model (the target output).
- `EvaluationExample`: (path, ground truth) pair for evaluation runs.
- `EvaluationResult`: Name + result + description for evaluation metrics.

## Project layout (relevant paths)

```
src/document_extraction_tools/
  base/            # abstract interfaces you implement
  config/          # config models + YAML loader
  runners/         # orchestrators (extraction + evaluation)
  types/           # shared data models
```

## How to implement your own extraction pipeline

### 1) Define your extraction schema

Create a Pydantic model that represents the structured data you want out of each document.

```python
from pydantic import BaseModel

class InvoiceSchema(BaseModel):
    invoice_id: str
    vendor: str
    total: float
```

### 2) Implement pipeline components

Subclass the base interfaces and implement the required methods.

```python
from document_extraction_tools.base import (
    BaseFileLister,
    BaseReader,
    BaseConverter,
    BaseExtractor,
    BaseExtractionExporter,
)
from document_extraction_tools.types import Document, DocumentBytes, PathIdentifier
from document_extraction_tools.config import (
    BaseFileListerConfig,
    BaseReaderConfig,
    BaseConverterConfig,
    BaseExtractorConfig,
    BaseExtractionExporterConfig,
)

class MyFileLister(BaseFileLister):
    def __init__(self, config: BaseFileListerConfig) -> None:
        super().__init__(config)

    def list_files(self) -> list[PathIdentifier]:
        return [PathIdentifier(path="/path/to/doc.pdf")]


class MyReader(BaseReader):
    def __init__(self, config: BaseReaderConfig) -> None:
        super().__init__(config)

    def read(self, path_identifier: PathIdentifier) -> DocumentBytes:
        with open(path_identifier.path, "rb") as f:
            return DocumentBytes(file_bytes=f.read(), path_identifier=path_identifier)


class MyConverter(BaseConverter):
    def __init__(self, config: BaseConverterConfig) -> None:
        super().__init__(config)

    def convert(self, document_bytes: DocumentBytes) -> Document:
        # Parse PDF, OCR, etc. and return a Document
        ...


class MyExtractor(BaseExtractor):
    def __init__(self, config: BaseExtractorConfig) -> None:
        super().__init__(config)

    async def extract(self, document: Document, schema: type[InvoiceSchema]) -> InvoiceSchema:
        # Call LLM or rules-based system
        ...


class MyExtractionExporter(BaseExtractionExporter):
    def __init__(self, config: BaseExtractionExporterConfig) -> None:
        super().__init__(config)

    async def export(self, document: Document, data: InvoiceSchema) -> None:
        # Persist data to DB, filesystem, etc.
        ...
```

### 3) Create configuration models and YAML files

Each component has a base config class with a default filename (e.g. `reader.yaml`).
Subclass the config models to add your own fields, then provide YAML files in
the directory you pass as `config_dir` to `load_config` (default is
`config/yaml/`).

Default filenames:

- `extraction_orchestrator.yaml`
- `file_lister.yaml`
- `reader.yaml`
- `converter.yaml`
- `extractor.yaml`
- `extraction_exporter.yaml`

Example YAML (`config/yaml/extractor.yaml`):

```yaml
# add fields your Extractor config defines
model_name: "gemini-3-flash-preview"
```

### 4) Load config and run the pipeline

```python
import asyncio
from document_extraction_tools.config import load_config
from document_extraction_tools.runners import ExtractionOrchestrator
from document_extraction_tools.config import ExtractionOrchestratorConfig

config = load_config(
    lister_config_cls=MyFileListerConfig,
    reader_config_cls=MyReaderConfig,
    converter_config_cls=MyConverterConfig,
    extractor_config_cls=MyExtractorConfig,
    exporter_config_cls=MyExtractionExporterConfig,
    orchestrator_config_cls=ExtractionOrchestratorConfig,
    config_dir=Path("config/yaml"),
)

orchestrator = ExtractionOrchestrator.from_config(
    config=config,
    schema=InvoiceSchema,
    reader_cls=MyReader,
    converter_cls=MyConverter,
    extractor_cls=MyExtractor,
    exporter_cls=MyExtractionExporter,
)

file_lister = MyFileLister(config.file_lister)
file_paths = file_lister.list_files()

asyncio.run(orchestrator.run(file_paths))
```

## How to implement an evaluation pipeline

The evaluation pipeline reuses your reader/converter/extractor and adds three pieces:

1. **TestDataLoader**: loads evaluation examples (file + ground truth)
2. **Evaluator(s)**: compute metrics for each example
3. **EvaluationExporter**: persist results

Required YAML filenames for evaluation:

- `evaluation_orchestrator.yaml`
- `test_data_loader.yaml`
- `evaluator.yaml` (one top-level key per evaluator config class name)
- `reader.yaml`
- `converter.yaml`
- `extractor.yaml`
- `evaluation_exporter.yaml`

Example usage:

```python
from document_extraction_tools.config import load_evaluation_config
from document_extraction_tools.runners import EvaluationOrchestrator
from document_extraction_tools.config import EvaluationOrchestratorConfig

config = load_evaluation_config(
    test_data_loader_config_cls=MyTestDataLoaderConfig,
    evaluator_config_classes=[MyEvaluatorConfig],
    reader_config_cls=MyReaderConfig,
    converter_config_cls=MyConverterConfig,
    extractor_config_cls=MyExtractorConfig,
    evaluation_exporter_config_cls=MyEvaluationExporterConfig,
    orchestrator_config_cls=EvaluationOrchestratorConfig,
    config_dir=Path("config/yaml"),
)

orchestrator = EvaluationOrchestrator.from_config(
    config=config,
    schema=InvoiceSchema,
    reader_cls=MyReader,
    converter_cls=MyConverter,
    extractor_cls=MyExtractor,
    test_data_loader_cls=MyTestDataLoader,
    evaluator_classes=[MyEvaluator],
    evaluation_exporter_cls=MyEvaluationExporter,
)

examples = MyTestDataLoader(config.test_data_loader).load_test_data(
    PathIdentifier(path="/path/to/eval-set")
)

asyncio.run(orchestrator.run(examples))
```

## Concurrency model

- **Reader + Converter** run in a thread pool (CPU-bound work).
- **Extractor + Exporter** run concurrently in the event loop (I/O-bound work).
- Tuning options live in `extraction_orchestrator.yaml` and `evaluation_orchestrator.yaml`:
  - `max_workers` (thread pool size)
  - `max_concurrency` (async I/O semaphore limit)

## Examples

We maintain a companion repo with concrete implementations built on top of this
module. It includes example pipelines and component implementations you can use
as reference: 

[document-extraction-examples](https://github.com/artefactory-uk/document-extraction-examples)

## Development

- Install dependencies: `uv sync`
- Run pre-commit: `uv run pre-commit run --all-files`
- Run tests: `uv run pytest`

## Contributing

Contributions are welcome. Please:

- Create a new branch using `feat/short-description`, `fix/short-description`, etc.
- Describe the change clearly in the PR description.
- Add or update tests in `tests/`.
- Run linting and tests before pushing: `uv run pre-commit run --all-files` and `uv run pytest`.
