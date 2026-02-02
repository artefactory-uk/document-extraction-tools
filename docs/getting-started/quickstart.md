# Quick Start

This guide walks you through building a simple document extraction pipeline.

## Overview

A document extraction pipeline consists of these stages:

1. **FileLister** - Discovers input files
2. **Reader** - Reads raw bytes from files
3. **Converter** - Converts bytes to structured documents
4. **Extractor** - Extracts structured data from documents
5. **Exporter** - Persists extracted data

## Step 1: Define Your Schema

First, define a Pydantic model for the data you want to extract. This example shows a lease schema similar to the [examples repository](https://github.com/artefactory-uk/document-extraction-examples):

```python
from pydantic import BaseModel, Field

class LeaseSchema(BaseModel):
    """Schema for extracted lease data."""

    landlord_name: str = Field(..., description="Full name of the landlord")
    tenant_name: str = Field(..., description="Full name of the tenant")
    property_address: str = Field(..., description="Address of the leased property")
    lease_start_date: str = Field(..., description="Lease start date (YYYY-MM-DD)")
    lease_end_date: str = Field(..., description="Lease end date (YYYY-MM-DD)")
    monthly_rent: float = Field(..., description="Monthly rent amount")
```

## Step 2: Implement Components

Implement each pipeline component by subclassing the base interfaces:

```python
from document_extraction_tools.base import (
    BaseFileLister,
    BaseReader,
    BaseConverter,
    BaseExtractor,
    BaseExtractionExporter,
)
from document_extraction_tools.types import Document, DocumentBytes, PathIdentifier


class MyFileLister(BaseFileLister):
    def list_files(self) -> list[PathIdentifier]:
        # Return list of files to process
        return [
            PathIdentifier(path="/data/lease1.pdf"),
            PathIdentifier(path="/data/lease2.pdf"),
        ]


class MyReader(BaseReader):
    def read(self, path_identifier: PathIdentifier) -> DocumentBytes:
        with open(path_identifier.path, "rb") as f:
            return DocumentBytes(
                file_bytes=f.read(),
                mime_type="application/pdf",
                path_identifier=path_identifier,
            )


class MyConverter(BaseConverter):
    def convert(self, document_bytes: DocumentBytes) -> Document:
        # Convert PDF bytes to Document (use your PDF library)
        ...


class MyExtractor(BaseExtractor):
    async def extract(self, document: Document, schema: type[LeaseSchema]) -> LeaseSchema:
        # Extract data using LLM or rules-based system
        ...


class MyExtractionExporter(BaseExtractionExporter):
    async def export(self, document: Document, data: LeaseSchema) -> None:
        # Save to database, file, etc.
        print(f"Exported lease for: {data.tenant_name}")
```

## Step 3: Create Configuration

Create YAML configuration files in `config/yaml/`:

```yaml title="config/yaml/extraction_orchestrator.yaml"
max_workers: 4
max_concurrency: 10
```

## Step 4: Run the Pipeline

```python
import asyncio
from pathlib import Path
from document_extraction_tools.config import load_config, ExtractionOrchestratorConfig
from document_extraction_tools.runners import ExtractionOrchestrator

# Load configuration
config = load_config(
    lister_config_cls=MyFileListerConfig,
    reader_config_cls=MyReaderConfig,
    converter_config_cls=MyConverterConfig,
    extractor_config_cls=MyExtractorConfig,
    exporter_config_cls=MyExtractionExporterConfig,
    orchestrator_config_cls=ExtractionOrchestratorConfig,
    config_dir=Path("config/yaml"),
)

# Create orchestrator
orchestrator = ExtractionOrchestrator.from_config(
    config=config,
    schema=LeaseSchema,
    reader_cls=MyReader,
    converter_cls=MyConverter,
    extractor_cls=MyExtractor,
    exporter_cls=MyExtractionExporter,
)

# List files and run
file_lister = MyFileLister(config.file_lister)
file_paths = file_lister.list_files()

asyncio.run(orchestrator.run(file_paths))
```

## Next Steps

- Learn about [Data Models](../concepts/data-models.md)
- Understand the [Extraction Pipeline](../concepts/extraction-pipeline.md) in depth
- See the [Examples Repository](https://github.com/artefactory-uk/document-extraction-examples) for the complete Simple Lease Extraction implementation with Gemini
