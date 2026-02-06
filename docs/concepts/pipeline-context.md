# Pipeline Context

The `PipelineContext` is a shared state container that flows through all pipeline components, enabling communication and data sharing across the extraction or evaluation process.

## Why Use PipelineContext?

Pipeline components are designed to be stateless and independent. However, real-world pipelines often need to:

- **Track execution metadata** - Run IDs, timestamps, batch identifiers
- **Share configuration** - Environment-specific settings, feature flags
- **Pass runtime state** - Accumulated metrics, processing hints
- **Enable observability** - Correlation IDs for logging and tracing

`PipelineContext` provides a clean way to share this information without coupling components together.

## Creating a Context

```python
from document_extraction_tools.types import PipelineContext

# Empty context (default)
context = PipelineContext()

# Context with initial values
context = PipelineContext(
    context={
        "run_id": "extraction-2024-01-15-001",
        "batch_size": 100,
    }
)
```

## Passing Context to the Pipeline

Pass the context when calling `orchestrator.run()`:

```python
from document_extraction_tools.runners import ExtractionOrchestrator
from document_extraction_tools.types import PipelineContext

# Create context
context = PipelineContext(
    context={
        "run_id": "daily-extraction-001",
    }
)

# Pass to orchestrator
await orchestrator.run(file_paths, context=context)
```

If no context is provided, an empty `PipelineContext()` is created automatically.

## Accessing Context in Components

Every component method receives an optional `context` parameter. Access values using the `context` dictionary:

### In a Reader

```python
from document_extraction_tools.base import BaseReader
from document_extraction_tools.types import DocumentBytes, PathIdentifier, PipelineContext


class MyReader(BaseReader):
    def read(
        self, path_identifier: PathIdentifier, context: PipelineContext | None = None
    ) -> DocumentBytes:
        # Access context values safely
        run_id = context.context.get("run_id") if context else None

        # Use for logging
        print(f"[{run_id}] Reading: {path_identifier.path}")

        with open(path_identifier.path, "rb") as f:
            return DocumentBytes(
                file_bytes=f.read(),
                path_identifier=path_identifier,
            )
```

### In an Extractor

```python
from document_extraction_tools.base import BaseExtractor
from document_extraction_tools.types import Document, ExtractionResult, PipelineContext


class MyExtractor(BaseExtractor):
    async def extract(
        self,
        document: Document,
        schema: type,
        context: PipelineContext | None = None,
    ) -> ExtractionResult:
        # Get environment-specific settings
        environment = context.context.get("environment", "development") if context else "development"

        # Adjust behavior based on context
        if environment == "production":
            # Use more conservative settings in production
            temperature = 0.0
        else:
            temperature = 0.1

        # Extract with the appropriate settings
        result = await self._call_llm(document, schema, temperature)
        return ExtractionResult(data=result)
```

### In an Exporter

```python
from document_extraction_tools.base import BaseExtractionExporter
from document_extraction_tools.types import Document, ExtractionResult, PipelineContext


class MyExporter(BaseExtractionExporter):
    async def export(
        self,
        document: Document,
        data: ExtractionResult,
        context: PipelineContext | None = None,
    ) -> None:
        # Include context metadata in exports
        run_id = context.context.get("run_id") if context else "unknown"

        output = {
            "run_id": run_id,
            "document_id": document.id,
            "data": data.data.model_dump(),
            "metadata": data.metadata,
        }

        await self._save_to_database(output)
```

## Common Use Cases

### 1. Run Tracking and Logging

```python
import uuid
from datetime import datetime

context = PipelineContext(
    context={
        "run_id": str(uuid.uuid4()),
        "started_at": datetime.now().isoformat(),
    }
)
```

### 2. Batch Processing Metadata

```python
context = PipelineContext(
    context={
        "batch_id": "batch-2024-01-15",
        "total_documents": len(file_paths),
    }
)
```

### 3. Correlation IDs for Distributed Tracing

```python
context = PipelineContext(
    context={
        "correlation_id": request_id,  # From incoming request
        "trace_id": span.trace_id,     # From tracing system
        "span_id": span.span_id,
    }
)
```

## Modifying Context During Execution

While `PipelineContext` is passed to all components, it's designed for **read-mostly** access. Components can read values but should be careful about modifications since multiple documents may be processed concurrently.

If you need to accumulate state (like metrics), consider using thread-safe structures:

```python
from threading import Lock
from document_extraction_tools.types import PipelineContext


# Create context with thread-safe counter
class ThreadSafeCounter:
    def __init__(self) -> None:
        self._count = 0
        self._lock = Lock()

    def increment(self) -> int:
        with self._lock:
            self._count += 1
            return self._count


context = PipelineContext(
    context={
        "processed_counter": ThreadSafeCounter(),
    }
)

# In a component
counter = context.context.get("processed_counter")
if counter:
    count = counter.increment()
    print(f"Processed document #{count}")
```

## Best Practices

### Do

- Use descriptive key names (`run_id` not `id`)
- Provide default values when accessing (`context.context.get("key", default)`)
- Always check if context is `None` before accessing
- Keep context values serializable when possible (for logging/debugging)
- Use context for cross-cutting concerns (logging, tracing, configuration)

### Don't

- Store large objects (file contents, model instances) in context
- Rely on context for component-specific configuration (use config classes instead)
- Mutate context values in components without thread safety
- Use context to pass data that should flow through the pipeline types (use `metadata` fields instead)

## Context vs Component Config

| Use Context For | Use Config For |
|-----------------|----------------|
| Runtime values (run IDs, timestamps) | Static settings (model names, paths) |
| Cross-cutting concerns (logging, tracing) | Component-specific parameters |
| Values that change per-run | Environment variables, feature flags |
| Correlation IDs, batch metadata | Values that change per-deployment |

## API Reference

::: document_extraction_tools.types.PipelineContext
    options:
      show_root_heading: false
      heading_level: 3
      members: true
      show_source: false
