# Evaluation Pipeline

The evaluation pipeline measures extraction quality against ground truth data.

## Pipeline Flow

```mermaid
flowchart LR
    subgraph Input
        TDL[TestDataLoader]
    end

    subgraph ThreadPool["Thread Pool (CPU-bound)"]
        R[Reader]
        C[Converter]
        EV[Evaluators]
    end

    subgraph AsyncIO["Async Event Loop (I/O-bound)"]
        E[Extractor]
    end

    subgraph Output
        EX[Exporter]
    end

    TDL -->|"list[EvaluationExample]"| R
    R -->|DocumentBytes| C
    C -->|Document| E
    E -->|ExtractionResult| EV
    TDL -.->|GroundTruth| EV
    EV -->|"list[EvaluationResult]"| EX
    EX -->|Persisted| Storage[(Storage)]
```

## Per-Example Processing

For each evaluation example, the orchestrator runs:

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant TP as Thread Pool
    participant R as Reader
    participant C as Converter
    participant E as Extractor
    participant EV as Evaluators
    participant EX as Exporter

    Note over O: EvaluationExample contains<br/>PathIdentifier + GroundTruth
    Note over O: PipelineContext passed to all components

    O->>TP: Submit ingest task
    TP->>R: read(path_identifier, context)
    R-->>TP: DocumentBytes
    TP->>C: convert(document_bytes, context)
    C-->>TP: Document
    TP-->>O: Document

    O->>E: extract(document, schema, context)
    Note over E: Async I/O (e.g., LLM API call)
    E-->>O: ExtractionResult

    O->>TP: Submit evaluation tasks
    TP->>EV: evaluate(ground_truth, prediction)
    EV-->>TP: EvaluationResult
    TP-->>O: list[EvaluationResult]

    Note over O: After all examples complete
    O->>EX: export(all_results, context)
    Note over EX: Async I/O
    EX-->>O: Done
```

## Components

### 1. TestDataLoader

Loads evaluation examples (ground truth + file paths). Called **before** the orchestrator runs.

```python
from document_extraction_tools.base import BaseTestDataLoader
from document_extraction_tools.types import EvaluationExample, ExtractionResult, PathIdentifier

class MyTestDataLoader(BaseTestDataLoader[InvoiceSchema]):
    def load_test_data(
        self, path_identifier: PathIdentifier
    ) -> list[EvaluationExample[InvoiceSchema]]:
        # Load from JSON, CSV, database, etc.
        examples = []
        for row in load_ground_truth_data():
            examples.append(EvaluationExample(
                id=row["file_path"],
                path_identifier=PathIdentifier(path=row["file_path"]),
                true=ExtractionResult(data=InvoiceSchema(**row["true"])),
            ))
        return examples
```

### 2. Evaluator

Computes metrics by comparing ground truth vs predictions. Runs in the **thread pool**.

```python
from document_extraction_tools.base import BaseEvaluator
from document_extraction_tools.types import EvaluationResult, ExtractionResult, PipelineContext

class FieldAccuracyEvaluator(BaseEvaluator[InvoiceSchema]):
    def evaluate(
        self,
        true: ExtractionResult[InvoiceSchema],
        pred: ExtractionResult[InvoiceSchema],
        context: PipelineContext | None = None,
    ) -> EvaluationResult:
        # Compare fields
        total_fields = len(true.data.model_fields)
        correct = sum(
            1 for field in true.data.model_fields
            if getattr(true.data, field) == getattr(pred.data, field)
        )

        return EvaluationResult(
            name="field_accuracy",
            result=correct / total_fields,
            description="Percentage of fields correctly extracted"
        )
```

### 3. EvaluationExporter

Persists evaluation results. Called **once** after all examples are processed. Runs in the **async event loop**.

```python
from document_extraction_tools.base import BaseEvaluationExporter
from document_extraction_tools.types import Document, EvaluationResult

class MyEvaluationExporter(BaseEvaluationExporter):
    async def export(
        self, results: list[tuple[Document, list[EvaluationResult]]]
    ) -> None:
        # Save to file, database, monitoring system, etc.
        for document, eval_results in results:
            for result in eval_results:
                print(f"{document.path_identifier.path}: {result.name}={result.result}")
```

## Multiple Evaluators

You can run multiple evaluators to compute different metrics:

```mermaid
flowchart LR
    subgraph Evaluators
        E1[FieldAccuracyEvaluator]
        E2[LevenshteinEvaluator]
        E3[NumericToleranceEvaluator]
    end

    GT[GroundTruth] --> E1 & E2 & E3
    Pred[Prediction] --> E1 & E2 & E3

    E1 --> R1[EvaluationResult]
    E2 --> R2[EvaluationResult]
    E3 --> R3[EvaluationResult]
```

```python
evaluator_classes = [
    FieldAccuracyEvaluator,
    LevenshteinDistanceEvaluator,
    NumericToleranceEvaluator,
]

orchestrator = EvaluationOrchestrator.from_config(
    config=config,
    schema=InvoiceSchema,
    reader_cls=MyReader,
    converter_cls=MyConverter,
    extractor_cls=MyExtractor,
    test_data_loader_cls=MyTestDataLoader,
    evaluator_classes=evaluator_classes,
    evaluation_exporter_cls=MyEvaluationExporter,
)
```

## Concurrency Model

```mermaid
flowchart TB
    subgraph "Orchestrator.run(examples)"
        direction TB
        TP["ThreadPoolExecutor<br/>max_workers"]
        SEM["Semaphore<br/>max_concurrency"]

        subgraph "Per Example Task"
            I["Ingest: Read + Convert"]
            EX["Extract"]
            EV["Evaluate (all evaluators)"]
        end

        TP -.->|"CPU-bound"| I
        SEM -.->|"I/O-bound"| EX
        TP -.->|"CPU-bound"| EV

        subgraph "After All Examples"
            Export["Export all results"]
        end
    end
```

| Stage | Execution Model | Reason |
|-------|-----------------|--------|
| Reader | Thread pool | File I/O is blocking |
| Converter | Thread pool | CPU-bound parsing |
| Extractor | Async | Network I/O (LLM calls) |
| Evaluators | Thread pool | CPU-bound comparison |
| Exporter | Async | Network/disk I/O |

## Running Evaluation

```python
import uuid
from document_extraction_tools.config import load_evaluation_config
from document_extraction_tools.runners import EvaluationOrchestrator
from document_extraction_tools.types import PipelineContext

config = load_evaluation_config(
    test_data_loader_config_cls=MyTestDataLoaderConfig,
    evaluator_config_classes=[FieldAccuracyEvaluatorConfig],
    reader_config_cls=MyReaderConfig,
    converter_config_cls=MyConverterConfig,
    extractor_config_cls=MyExtractorConfig,
    evaluation_exporter_config_cls=MyEvaluationExporterConfig,
)

orchestrator = EvaluationOrchestrator.from_config(...)

# Load test data
examples = MyTestDataLoader(config).load_test_data(
    PathIdentifier(path="/path/to/eval-set")
)

# Run evaluation with optional context
context = PipelineContext(context={"run_id": str(uuid.uuid4())[:8]})
await orchestrator.run(examples, context=context)
```
