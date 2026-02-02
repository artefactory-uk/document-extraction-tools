# Implementing an Extraction Pipeline

This guide walks through implementing a complete extraction pipeline.

## Prerequisites

- Document Extraction Tools installed
- Understanding of [Core Concepts](../concepts/overview.md)
- A clear definition of what data you want to extract

## Step 1: Define Your Extraction Schema

Start by defining a Pydantic model for your target output:

```python
from pydantic import BaseModel, Field

class InvoiceSchema(BaseModel):
    """Schema for extracted invoice data."""

    invoice_id: str = Field(
        ...,
        description="Unique invoice identifier"
    )
    vendor: str = Field(
        ...,
        description="Vendor or issuer name"
    )
    total: float = Field(
        ...,
        description="Total invoice amount"
    )
    currency: str = Field(
        default="USD",
        description="Currency code"
    )
    line_items: list[LineItem] = Field(
        default_factory=list,
        description="Individual line items"
    )


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
```

!!! tip "Schema Design Tips"
    - Use descriptive `Field` descriptions - they help LLM extractors
    - Set sensible defaults for optional fields
    - Break complex structures into nested models

## Step 2: Implement Pipeline Components

### FileLister

```python
from pathlib import Path
from document_extraction_tools.base import BaseFileLister
from document_extraction_tools.config import BaseFileListerConfig
from document_extraction_tools.types import PathIdentifier


class LocalFileListerConfig(BaseFileListerConfig):
    input_directory: str
    file_pattern: str = "*.pdf"


class LocalFileLister(BaseFileLister):
    def __init__(self, config: LocalFileListerConfig) -> None:
        super().__init__(config)
        self.config = config

    def list_files(self) -> list[PathIdentifier]:
        directory = Path(self.config.input_directory)
        return [
            PathIdentifier(path=str(p))
            for p in directory.glob(self.config.file_pattern)
        ]
```

### Reader

```python
from document_extraction_tools.base import BaseReader
from document_extraction_tools.config import BaseReaderConfig
from document_extraction_tools.types import DocumentBytes, PathIdentifier


class LocalReaderConfig(BaseReaderConfig):
    pass  # No additional config needed


class LocalReader(BaseReader):
    def __init__(self, config: LocalReaderConfig) -> None:
        super().__init__(config)

    def read(self, path_identifier: PathIdentifier) -> DocumentBytes:
        path = Path(path_identifier.path)

        # Determine MIME type
        mime_types = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
        }
        mime_type = mime_types.get(path.suffix.lower(), "application/octet-stream")

        with open(path, "rb") as f:
            return DocumentBytes(
                bytes=f.read(),
                mime_type=mime_type,
                path_identifier=path_identifier
            )
```

### Converter

```python
from document_extraction_tools.base import BaseConverter
from document_extraction_tools.config import BaseConverterConfig
from document_extraction_tools.types import Document, DocumentBytes, Page


class PDFConverterConfig(BaseConverterConfig):
    dpi: int = 300


class PDFConverter(BaseConverter):
    def __init__(self, config: PDFConverterConfig) -> None:
        super().__init__(config)
        self.config = config

    def convert(self, document_bytes: DocumentBytes) -> Document:
        # Use your preferred PDF library (pypdf, pymupdf, etc.)
        pages = self._parse_pdf(document_bytes.bytes)

        return Document(
            path_identifier=document_bytes.path_identifier,
            pages=pages,
            metadata={"page_count": len(pages)},
            content_type="image"
        )

    def _parse_pdf(self, pdf_bytes: bytes) -> list[Page]:
        # Implementation depends on your PDF library
        ...
```

### Extractor

```python
from document_extraction_tools.base import BaseExtractor
from document_extraction_tools.config import BaseExtractorConfig
from document_extraction_tools.types import Document


class LLMExtractorConfig(BaseExtractorConfig):
    model_name: str
    temperature: float = 0.0


class LLMExtractor(BaseExtractor):
    def __init__(self, config: LLMExtractorConfig) -> None:
        super().__init__(config)
        self.config = config
        self.client = create_llm_client(config.model_name)

    async def extract(
        self, document: Document, schema: type[InvoiceSchema]
    ) -> InvoiceSchema:
        # Build prompt from document pages
        prompt = self._build_prompt(document, schema)

        # Call LLM
        response = await self.client.generate(
            prompt=prompt,
            temperature=self.config.temperature,
        )

        # Parse and validate response
        return schema.model_validate_json(response)

    def _build_prompt(self, document: Document, schema: type) -> str:
        # Build extraction prompt with document content and schema
        ...
```

### Exporter

```python
import json
from pathlib import Path
from document_extraction_tools.base import BaseExtractionExporter
from document_extraction_tools.config import BaseExtractionExporterConfig
from document_extraction_tools.types import Document


class JSONExporterConfig(BaseExtractionExporterConfig):
    output_directory: str


class JSONExporter(BaseExtractionExporter):
    def __init__(self, config: JSONExporterConfig) -> None:
        super().__init__(config)
        self.config = config

    async def export(self, document: Document, data: InvoiceSchema) -> None:
        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create output filename from input
        input_name = Path(document.path_identifier.path).stem
        output_path = output_dir / f"{input_name}.json"

        with open(output_path, "w") as f:
            json.dump(data.model_dump(), f, indent=2)
```

## Step 3: Create Configuration Files

```yaml title="config/yaml/file_lister.yaml"
input_directory: "./data/invoices"
file_pattern: "*.pdf"
```

```yaml title="config/yaml/converter.yaml"
dpi: 300
```

```yaml title="config/yaml/extractor.yaml"
model_name: "gpt-4"
temperature: 0.0
```

```yaml title="config/yaml/extraction_exporter.yaml"
output_directory: "./output/extractions"
```

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

async def main():
    # Load configuration
    config = load_config(
        lister_config_cls=LocalFileListerConfig,
        reader_config_cls=LocalReaderConfig,
        converter_config_cls=PDFConverterConfig,
        extractor_config_cls=LLMExtractorConfig,
        exporter_config_cls=JSONExporterConfig,
        orchestrator_config_cls=ExtractionOrchestratorConfig,
        config_dir=Path("config/yaml"),
    )

    # Create orchestrator
    orchestrator = ExtractionOrchestrator.from_config(
        config=config,
        schema=InvoiceSchema,
        reader_cls=LocalReader,
        converter_cls=PDFConverter,
        extractor_cls=LLMExtractor,
        exporter_cls=JSONExporter,
    )

    # List files
    file_lister = LocalFileLister(config.file_lister)
    file_paths = file_lister.list_files()

    print(f"Processing {len(file_paths)} files...")

    # Run pipeline
    await orchestrator.run(file_paths)

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Add [Evaluation](implementing-evaluation.md) to measure extraction quality
- See the [Examples Repository](https://github.com/artefactory-uk/document-extraction-examples) for complete implementations
