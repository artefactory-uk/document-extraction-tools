# Base Classes

Abstract base classes that define the interfaces for pipeline components.

## Extraction Pipeline

### BaseFileLister

::: document_extraction_tools.base.BaseFileLister
    options:
      show_root_heading: false
      heading_level: 4

### BaseReader

::: document_extraction_tools.base.BaseReader
    options:
      show_root_heading: false
      heading_level: 4

### BaseConverter

::: document_extraction_tools.base.BaseConverter
    options:
      show_root_heading: false
      heading_level: 4

### BaseExtractor

::: document_extraction_tools.base.BaseExtractor
    options:
      show_root_heading: false
      heading_level: 4

### BaseExtractionExporter

::: document_extraction_tools.base.BaseExtractionExporter
    options:
      show_root_heading: false
      heading_level: 4

## Evaluation Pipeline

### BaseTestDataLoader

::: document_extraction_tools.base.BaseTestDataLoader
    options:
      show_root_heading: false
      heading_level: 4

### BaseEvaluator

::: document_extraction_tools.base.BaseEvaluator
    options:
      show_root_heading: false
      heading_level: 4

### BaseEvaluationExporter

::: document_extraction_tools.base.BaseEvaluationExporter
    options:
      show_root_heading: false
      heading_level: 4

## Orchestrators

### ExtractionOrchestrator

::: document_extraction_tools.runners.ExtractionOrchestrator
    options:
      show_root_heading: false
      heading_level: 4

### EvaluationOrchestrator

::: document_extraction_tools.runners.EvaluationOrchestrator
    options:
      show_root_heading: false
      heading_level: 4

## Import Shortcuts

All base classes can be imported from the top-level `base` module:

```python
from document_extraction_tools.base import (
    BaseFileLister,
    BaseReader,
    BaseConverter,
    BaseExtractor,
    BaseExtractionExporter,
    BaseTestDataLoader,
    BaseEvaluator,
    BaseEvaluationExporter,
)
```
