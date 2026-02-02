# Implementing an Extraction Pipeline

This guide walks through implementing a complete extraction pipeline.

## Prerequisites

- Document Extraction Tools installed
- Understanding of [Core Concepts](../concepts/overview.md)
- A clear definition of what data you want to extract

## Step 1: Define Your Extraction Schema

Start by defining a Pydantic model for your target output. This example shows a lease details schema similar to the [examples repository](https://github.com/artefactory-uk/document-extraction-examples):

```python
from pydantic import BaseModel, Field

class Address(BaseModel):
    """Property address details."""

    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State or region")
    postal_code: str = Field(..., description="Postal/ZIP code")


class LeaseSchema(BaseModel):
    """Schema for extracted lease data."""

    landlord_name: str = Field(
        ...,
        description="Full name of the landlord or property owner"
    )
    tenant_name: str = Field(
        ...,
        description="Full name of the tenant"
    )
    property_address: Address = Field(
        ...,
        description="Address of the leased property"
    )
    lease_start_date: str = Field(
        ...,
        description="Start date of the lease in YYYY-MM-DD format"
    )
    lease_end_date: str = Field(
        ...,
        description="End date of the lease in YYYY-MM-DD format"
    )
    monthly_rent: float = Field(
        ...,
        description="Monthly rent amount"
    )
    security_deposit: float = Field(
        default=0.0,
        description="Security deposit amount"
    )
    currency: str = Field(
        default="USD",
        description="Currency code"
    )
```

!!! tip "Schema Design Tips"
    - Use descriptive `Field` descriptions - they help LLM extractors understand what to extract
    - Set sensible defaults for optional fields
    - Break complex structures into nested models (like `Address` above)
    - Use standard date formats (ISO 8601) for date fields

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
                file_bytes=f.read(),
                mime_type=mime_type,
                path_identifier=path_identifier,
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
        pages = self._parse_pdf(document_bytes.file_bytes)

        return Document(
            id=str(document_bytes.path_identifier.path),
            path_identifier=document_bytes.path_identifier,
            pages=pages,
            metadata={"page_count": len(pages)},
            content_type="image",
        )

    def _parse_pdf(self, pdf_bytes: bytes) -> list[Page]:
        # Implementation depends on your PDF library
        ...
```

### Extractor

This example shows a Gemini-based extractor similar to the [examples repository](https://github.com/artefactory-uk/document-extraction-examples):

```python
import google.generativeai as genai
from document_extraction_tools.base import BaseExtractor
from document_extraction_tools.config import BaseExtractorConfig
from document_extraction_tools.types import Document


class GeminiExtractorConfig(BaseExtractorConfig):
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.0


class GeminiImageExtractor(BaseExtractor):
    def __init__(self, config: GeminiExtractorConfig) -> None:
        super().__init__(config)
        self.config = config
        self.model = genai.GenerativeModel(config.model_name)

    async def extract(
        self, document: Document, schema: type[LeaseSchema]
    ) -> LeaseSchema:
        # Build prompt with schema description
        prompt = self._build_prompt(schema)

        # Prepare image parts from document pages
        parts = [prompt]
        for page in document.pages:
            if page.image:
                parts.append(page.image)

        # Call Gemini with images
        response = await self.model.generate_content_async(
            parts,
            generation_config=genai.GenerationConfig(
                temperature=self.config.temperature,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        # Parse and validate response
        return schema.model_validate_json(response.text)

    def _build_prompt(self, schema: type) -> str:
        return f"""Extract the following information from the lease document images.
Return a JSON object matching this schema:
{schema.model_json_schema()}

Be precise and extract exactly what is stated in the document."""
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

    async def export(self, document: Document, data: LeaseSchema) -> None:
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
input_directory: "./data/leases"
file_pattern: "*.pdf"
```

```yaml title="config/yaml/converter.yaml"
dpi: 300
```

```yaml title="config/yaml/extractor.yaml"
model_name: "gemini-1.5-flash"
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
        extractor_config_cls=GeminiExtractorConfig,
        exporter_config_cls=JSONExporterConfig,
        orchestrator_config_cls=ExtractionOrchestratorConfig,
        config_dir=Path("config/yaml"),
    )

    # Create orchestrator
    orchestrator = ExtractionOrchestrator.from_config(
        config=config,
        schema=LeaseSchema,
        reader_cls=LocalReader,
        converter_cls=PDFConverter,
        extractor_cls=GeminiImageExtractor,
        exporter_cls=JSONExporter,
    )

    # List files
    file_lister = LocalFileLister(config.file_lister)
    file_paths = file_lister.list_files()

    print(f"Processing {len(file_paths)} lease documents...")

    # Run pipeline
    await orchestrator.run(file_paths)

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Add [Evaluation](implementing-evaluation.md) to measure extraction quality
- See the [Examples Repository](https://github.com/artefactory-uk/document-extraction-examples) for the complete Simple Lease Extraction implementation
