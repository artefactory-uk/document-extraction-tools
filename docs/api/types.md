# Types

Core data types used throughout the library. These Pydantic models define the structure of data flowing through extraction and evaluation pipelines.

## Import

```python
from document_extraction_tools.types import (
    PathIdentifier,
    DocumentBytes,
    Document,
    Page,
    TextData,
    ImageData,
    ExtractionResult,
    EvaluationExample,
    EvaluationResult,
    ExtractionSchema,
    PipelineContext,
)
```

---

## PathIdentifier

A unified reference to a document source. Used to track where documents originate from.

::: document_extraction_tools.types.PathIdentifier
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import PathIdentifier

# Simple path reference
path_id = PathIdentifier(path="/data/leases/lease_001.pdf")

# With additional metadata (e.g., for cloud storage)
path_id = PathIdentifier(
    path="gs://my-bucket/documents/lease.pdf",
    metadata={"bucket": "my-bucket", "region": "us-central1"}
)
```

---

## DocumentBytes

A standardized container for raw document data in memory. This decouples extraction logic from storage sources.

::: document_extraction_tools.types.DocumentBytes
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import DocumentBytes, PathIdentifier

with open("lease.pdf", "rb") as f:
    doc_bytes = DocumentBytes(
        file_bytes=f.read(),
        path_identifier=PathIdentifier(path="lease.pdf"),
        metadata={"mime_type": "application/pdf"},
    )
```

---

## Document

The master object representing a fully parsed document with pages.

::: document_extraction_tools.types.Document
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import Document, Page, ImageData, PathIdentifier

document = Document(
    id="lease_001",
    content_type="image",
    pages=[
        Page(page_number=1, data=ImageData(content=image_bytes)),
        Page(page_number=2, data=ImageData(content=image_bytes_2)),
    ],
    path_identifier=PathIdentifier(path="/data/lease_001.pdf"),
    metadata={"page_count": 2, "source": "local"},
)
```

---

## Page

Represents a single page within a document.

::: document_extraction_tools.types.Page
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import Page, TextData, ImageData

# Text page
text_page = Page(page_number=1, data=TextData(content="Lease agreement..."))

# Image page
image_page = Page(page_number=1, data=ImageData(content=image_bytes))
```

---

## TextData

Encapsulates textual content extracted from a page.

::: document_extraction_tools.types.TextData
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

---

## ImageData

Encapsulates image content in various formats (bytes, PIL Image, or NumPy array).

::: document_extraction_tools.types.ImageData
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from PIL import Image
from document_extraction_tools.types import ImageData

# From bytes
image_data = ImageData(content=raw_bytes)

# From PIL Image
pil_image = Image.open("page.png")
image_data = ImageData(content=pil_image)

# From NumPy array
import numpy as np
np_array = np.array(pil_image)
image_data = ImageData(content=np_array)
```

---

## ExtractionSchema

A type variable representing any Pydantic model used as an extraction schema.

::: document_extraction_tools.types.ExtractionSchema
    options:
      show_root_heading: false
      heading_level: 3
      show_source: false

**Usage:**

```python
from pydantic import BaseModel, Field
from document_extraction_tools.types import ExtractionSchema

class LeaseSchema(BaseModel):
    """Your custom extraction schema."""
    landlord_name: str = Field(..., description="Landlord name")
    tenant_name: str = Field(..., description="Tenant name")
    monthly_rent: float = Field(..., description="Monthly rent")

# LeaseSchema can be used wherever ExtractionSchema is expected
```

---

## ExtractionResult

Wraps the extracted schema data along with optional metadata. This is the return type of the `BaseExtractor.extract()` method.

::: document_extraction_tools.types.ExtractionResult
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import ExtractionResult

# Create an extraction result with metadata
result = ExtractionResult(
    data=LeaseSchema(
        landlord_name="John Smith",
        tenant_name="Jane Doe",
        monthly_rent=2500.00,
    ),
    metadata={
        "model": "gpt-4",
        "tokens_used": 1234,
        "confidence": 0.95,
    },
)

# Access the extracted data
print(result.data.landlord_name)  # "John Smith"

# Access metadata
print(result.metadata.get("confidence"))  # 0.95
```

---

## PipelineContext

A shared context object that can be passed through pipeline components to maintain state or share information across the pipeline.

::: document_extraction_tools.types.PipelineContext
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import PipelineContext

# Create context with runtime values
context = PipelineContext(
    context={
        "run_id": "extraction-2024-01-15",
        "started_at": "2024-01-15T10:30:00",
    }
)

# Access context values in components
run_id = context.context.get("run_id")

# Pass to orchestrator.run()
await orchestrator.run(file_paths, context=context)
```

---

## EvaluationExample

Pairs a ground-truth schema with a source document for evaluation.

::: document_extraction_tools.types.EvaluationExample
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import EvaluationExample, ExtractionResult, PathIdentifier

example = EvaluationExample(
    id="lease_001",
    path_identifier=PathIdentifier(
        path="data/leases/lease_001.pdf",
        metadata={"source": "local", "mime_type": "application/pdf"},
    ),
    true=ExtractionResult(
        data=LeaseSchema(
            landlord_name="John Smith",
            tenant_name="Jane Doe",
            monthly_rent=2500.00,
        ),
    ),
)
```

---

## EvaluationResult

Represents a single evaluation result produced by an evaluator.

::: document_extraction_tools.types.EvaluationResult
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false

**Example:**

```python
from document_extraction_tools.types import EvaluationResult

result = EvaluationResult(
    name="field_accuracy",
    result=0.85,
    description="17/20 fields matched exactly",
)
```
