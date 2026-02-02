# Data Models

Document Extraction Tools uses strongly-typed Pydantic models throughout the pipeline.

## Core Types

### PathIdentifier

A uniform handle for file locations with optional context:

```python
from document_extraction_tools.types import PathIdentifier

path = PathIdentifier(
    path="/data/invoices/invoice_001.pdf",
    context={"source": "email", "received_date": "2024-01-15"}
)
```

### DocumentBytes

Raw bytes with MIME type and source information:

```python
from document_extraction_tools.types import DocumentBytes

doc_bytes = DocumentBytes(
    bytes=raw_bytes,
    mime_type="application/pdf",
    path_identifier=path_identifier,
)
```

### Document

Parsed document with pages, content, and metadata:

```python
from document_extraction_tools.types import Document, Page

document = Document(
    path_identifier=path_identifier,
    pages=[
        Page(
            page_number=1,
            text="Invoice #12345...",
            image=image_array,  # numpy array
        )
    ],
    metadata={"page_count": 1}
)
```

### ExtractionSchema

Your custom Pydantic model defining the target output structure:

```python
from pydantic import BaseModel, Field

class InvoiceSchema(BaseModel):
    invoice_id: str = Field(..., description="Unique invoice identifier")
    vendor: str = Field(..., description="Vendor name")
    total: float = Field(..., description="Total amount")
```

## Evaluation Types

### EvaluationExample

A ground truth + file path pair for evaluation:

```python
from document_extraction_tools.types import EvaluationExample

example = EvaluationExample(
    path_identifier=PathIdentifier(path="/data/test/invoice_001.pdf"),
    ground_truth=InvoiceSchema(
        invoice_id="12345",
        vendor="Acme Corp",
        total=1500.00
    )
)
```

### EvaluationResult

Result from an evaluator:

```python
from document_extraction_tools.types import EvaluationResult

result = EvaluationResult(
    name="field_accuracy",
    result=0.95,
    description="Percentage of fields correctly extracted"
)
```

## Type Safety

All models are Pydantic BaseModels, providing:

- **Validation** - Automatic type checking and coercion
- **Serialization** - Easy JSON/dict conversion
- **Documentation** - Field descriptions for clarity
- **IDE Support** - Full autocomplete and type hints
