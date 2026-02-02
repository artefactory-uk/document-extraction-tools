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
    file_bytes=raw_bytes,
    mime_type="application/pdf",
    path_identifier=path_identifier,
)
```

### TextData

Encapsulates textual content for a page:

```python
from document_extraction_tools.types import TextData

text_data = TextData(content="Invoice #12345...")
```

### ImageData

Encapsulates image content in various formats (bytes, PIL Image, or NumPy array):

```python
from document_extraction_tools.types import ImageData

# From raw bytes
image_data = ImageData(content=raw_image_bytes)

# Or from PIL Image
from PIL import Image
image_data = ImageData(content=Image.open("page.png"))

# Or from NumPy array
import numpy as np
image_data = ImageData(content=np.array(...))
```

### Page

Represents a single page within a document:

```python
from document_extraction_tools.types import Page, TextData, ImageData

# Text page
text_page = Page(
    page_number=1,
    data=TextData(content="Invoice #12345..."),
)

# Image page
image_page = Page(
    page_number=1,
    data=ImageData(content=image_bytes),
)
```

### Document

Parsed document with pages, content, and metadata:

```python
from document_extraction_tools.types import Document, Page, TextData

document = Document(
    id="doc-001",
    path_identifier=path_identifier,
    pages=[
        Page(
            page_number=1,
            data=TextData(content="Invoice #12345..."),
        )
    ],
    content_type="text",
    metadata={"page_count": 1},
)
```

!!! note "Content Type Validation"
    The `Document` model validates that all page data types match the declared `content_type`. If `content_type` is `"text"`, all pages must contain `TextData`. If `content_type` is `"image"`, all pages must contain `ImageData`.

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
    id="/data/test/invoice_001.pdf",
    path_identifier=PathIdentifier(path="/data/test/invoice_001.pdf"),
    true=InvoiceSchema(
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
