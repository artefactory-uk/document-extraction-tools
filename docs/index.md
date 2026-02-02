# Document Extraction Tools

A modular, high-performance toolkit for building document extraction pipelines.

---

## What is Document Extraction Tools?

Document Extraction Tools provides clear interfaces for every stage of a document extraction pipeline, plus orchestrators that wire the stages together with async I/O and CPU-bound parallelism.

This library is intentionally implementation-light: you plug in your own components (readers, converters, extractors, exporters, evaluators) for each specific document type or data source.

## Key Features

- **Consistent Interfaces** - A unified set of interfaces for the entire document-extraction lifecycle
- **Typed Data Models** - Strong typing for documents, pages, and extraction results
- **Concurrent Orchestration** - Run extraction and evaluation pipelines concurrently and safely
- **Flexible Configuration** - Pydantic + YAML configuration system for repeatable pipelines

## Quick Example

```python
from document_extraction_tools.runners import ExtractionOrchestrator

# Configure and run your pipeline
orchestrator = ExtractionOrchestrator.from_config(
    config=config,
    schema=LeaseSchema,  # Your Pydantic schema
    reader_cls=LocalReader,
    converter_cls=PDFToImageConverter,
    extractor_cls=GeminiImageExtractor,
    exporter_cls=JSONExporter,
)

await orchestrator.run(file_paths)
```

## Getting Started

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install document-extraction-tools with pip or uv

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Build your first extraction pipeline

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-book-open-variant:{ .lg .middle } **Core Concepts**

    ---

    Understand the architecture and components

    [:octicons-arrow-right-24: Concepts](concepts/overview.md)

-   :material-github:{ .lg .middle } **Examples**

    ---

    See full working examples

    [:octicons-arrow-right-24: Examples Repository](https://github.com/artefactory-uk/document-extraction-examples)

</div>

## Project Layout

```
.
├── src/document_extraction_tools/
│   ├── base/           # Abstract base classes you implement
│   ├── config/         # Pydantic configs + YAML loader helpers
│   ├── runners/        # Orchestrators that run pipelines
│   └── types/          # Shared models/types
├── tests/
├── pyproject.toml
└── README.md
```
