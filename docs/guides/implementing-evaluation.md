# Implementing an Evaluation Pipeline

This guide walks through setting up evaluation to measure extraction quality.

## Prerequisites

- A working [Extraction Pipeline](implementing-extraction.md)
- Ground truth data for your documents
- Understanding of relevant metrics for your use case

## Step 1: Prepare Ground Truth Data

Create a dataset with known correct extractions:

```json title="data/evaluation/ground_truth.json"
[
  {
    "file_path": "data/invoices/invoice_001.pdf",
    "ground_truth": {
      "invoice_id": "INV-2024-001",
      "vendor": "Acme Corporation",
      "total": 1500.00,
      "currency": "USD"
    }
  },
  {
    "file_path": "data/invoices/invoice_002.pdf",
    "ground_truth": {
      "invoice_id": "INV-2024-002",
      "vendor": "Tech Solutions Inc",
      "total": 3250.75,
      "currency": "USD"
    }
  }
]
```

## Step 2: Implement TestDataLoader

```python
import json
from pathlib import Path
from document_extraction_tools.base import BaseTestDataLoader
from document_extraction_tools.config import BaseTestDataLoaderConfig
from document_extraction_tools.types import EvaluationExample, PathIdentifier


class JSONTestDataLoaderConfig(BaseTestDataLoaderConfig):
    pass  # Uses path_identifier to find the JSON file


class JSONTestDataLoader(BaseTestDataLoader[InvoiceSchema]):
    def __init__(self, config: JSONTestDataLoaderConfig) -> None:
        super().__init__(config)

    def load_test_data(
        self, path_identifier: PathIdentifier
    ) -> list[EvaluationExample[InvoiceSchema]]:
        with open(path_identifier.path) as f:
            data = json.load(f)

        examples = []
        for item in data:
            examples.append(EvaluationExample(
                id=item["file_path"],
                path_identifier=PathIdentifier(path=item["file_path"]),
                true=InvoiceSchema(**item["ground_truth"])
            ))

        return examples
```

## Step 3: Implement Evaluators

Create one or more evaluators to measure different aspects of quality.

### Field Accuracy Evaluator

```python
from document_extraction_tools.base import BaseEvaluator
from document_extraction_tools.config import BaseEvaluatorConfig
from document_extraction_tools.types import EvaluationResult


class FieldAccuracyEvaluatorConfig(BaseEvaluatorConfig):
    pass


class FieldAccuracyEvaluator(BaseEvaluator[InvoiceSchema]):
    """Measures percentage of fields that exactly match."""

    def __init__(self, config: FieldAccuracyEvaluatorConfig) -> None:
        super().__init__(config)

    def evaluate(
        self, true: InvoiceSchema, pred: InvoiceSchema
    ) -> EvaluationResult:
        fields = list(true.model_fields.keys())
        correct = sum(
            1 for field in fields
            if getattr(true, field) == getattr(pred, field)
        )

        accuracy = correct / len(fields) if fields else 0.0

        return EvaluationResult(
            name="field_accuracy",
            result=accuracy,
            description=f"{correct}/{len(fields)} fields correct"
        )
```

### Numeric Tolerance Evaluator

```python
class NumericToleranceEvaluatorConfig(BaseEvaluatorConfig):
    tolerance: float = 0.01  # 1% tolerance


class NumericToleranceEvaluator(BaseEvaluator[InvoiceSchema]):
    """Checks if numeric fields are within tolerance."""

    def __init__(self, config: NumericToleranceEvaluatorConfig) -> None:
        super().__init__(config)
        self.config = config

    def evaluate(
        self, true: InvoiceSchema, pred: InvoiceSchema
    ) -> EvaluationResult:
        # Check total field
        if true.total == 0:
            within_tolerance = pred.total == 0
        else:
            relative_error = abs(true.total - pred.total) / true.total
            within_tolerance = relative_error <= self.config.tolerance

        return EvaluationResult(
            name="total_within_tolerance",
            result=1.0 if within_tolerance else 0.0,
            description=f"Total {'within' if within_tolerance else 'outside'} {self.config.tolerance:.1%} tolerance"
        )
```

### String Similarity Evaluator

```python
from difflib import SequenceMatcher


class StringSimilarityEvaluatorConfig(BaseEvaluatorConfig):
    field_name: str = "vendor"


class StringSimilarityEvaluator(BaseEvaluator[InvoiceSchema]):
    """Measures string similarity for a specific field."""

    def __init__(self, config: StringSimilarityEvaluatorConfig) -> None:
        super().__init__(config)
        self.config = config

    def evaluate(
        self, true: InvoiceSchema, pred: InvoiceSchema
    ) -> EvaluationResult:
        true_value = getattr(true, self.config.field_name, "")
        pred_value = getattr(pred, self.config.field_name, "")

        similarity = SequenceMatcher(
            None,
            true_value.lower(),
            pred_value.lower()
        ).ratio()

        return EvaluationResult(
            name=f"{self.config.field_name}_similarity",
            result=similarity,
            description=f"String similarity: {similarity:.2%}"
        )
```

## Step 4: Implement EvaluationExporter

```python
import csv
from pathlib import Path
from document_extraction_tools.base import BaseEvaluationExporter
from document_extraction_tools.config import BaseEvaluationExporterConfig
from document_extraction_tools.types import Document, EvaluationResult


class CSVEvaluationExporterConfig(BaseEvaluationExporterConfig):
    output_path: str


class CSVEvaluationExporter(BaseEvaluationExporter):
    def __init__(self, config: CSVEvaluationExporterConfig) -> None:
        super().__init__(config)
        self.config = config

    async def export(
        self, results: list[tuple[Document, list[EvaluationResult]]]
    ) -> None:
        output_path = Path(self.config.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Collect all metric names
        all_metrics = set()
        for _, eval_results in results:
            for result in eval_results:
                all_metrics.add(result.name)

        # Write CSV
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["file"] + sorted(all_metrics))

            # Data rows
            for document, eval_results in results:
                row = [document.path_identifier.path]
                metrics = {r.name: r.result for r in eval_results}
                for metric in sorted(all_metrics):
                    row.append(metrics.get(metric, ""))
                writer.writerow(row)

        # Print summary
        print(f"\nEvaluation Results Summary:")
        print(f"{'Metric':<30} {'Mean':>10} {'Min':>10} {'Max':>10}")
        print("-" * 62)

        for metric in sorted(all_metrics):
            values = [
                r.result for _, results in results
                for r in results if r.name == metric
            ]
            if values:
                print(f"{metric:<30} {sum(values)/len(values):>10.3f} {min(values):>10.3f} {max(values):>10.3f}")
```

## Step 5: Create Configuration Files

```yaml title="config/yaml/evaluator.yaml"
FieldAccuracyEvaluatorConfig: {}

NumericToleranceEvaluatorConfig:
  tolerance: 0.01

StringSimilarityEvaluatorConfig:
  field_name: "vendor"
```

```yaml title="config/yaml/evaluation_exporter.yaml"
output_path: "./output/evaluation_results.csv"
```

```yaml title="config/yaml/evaluation_orchestrator.yaml"
max_workers: 4
max_concurrency: 10
```

## Step 6: Run Evaluation

```python
import asyncio
from pathlib import Path
from document_extraction_tools.config import (
    load_evaluation_config,
    EvaluationOrchestratorConfig,
)
from document_extraction_tools.runners import EvaluationOrchestrator
from document_extraction_tools.types import PathIdentifier

async def main():
    # Load configuration
    config = load_evaluation_config(
        test_data_loader_config_cls=JSONTestDataLoaderConfig,
        evaluator_config_classes=[
            FieldAccuracyEvaluatorConfig,
            NumericToleranceEvaluatorConfig,
            StringSimilarityEvaluatorConfig,
        ],
        reader_config_cls=LocalReaderConfig,
        converter_config_cls=PDFConverterConfig,
        extractor_config_cls=LLMExtractorConfig,
        evaluation_exporter_config_cls=CSVEvaluationExporterConfig,
        orchestrator_config_cls=EvaluationOrchestratorConfig,
        config_dir=Path("config/yaml"),
    )

    # Create orchestrator
    orchestrator = EvaluationOrchestrator.from_config(
        config=config,
        schema=InvoiceSchema,
        reader_cls=LocalReader,
        converter_cls=PDFConverter,
        extractor_cls=LLMExtractor,
        test_data_loader_cls=JSONTestDataLoader,
        evaluator_classes=[
            FieldAccuracyEvaluator,
            NumericToleranceEvaluator,
            StringSimilarityEvaluator,
        ],
        evaluation_exporter_cls=CSVEvaluationExporter,
    )

    # Load test data
    test_data_loader = JSONTestDataLoader(config.test_data_loader)
    examples = test_data_loader.load_test_data(
        PathIdentifier(path="data/evaluation/ground_truth.json")
    )

    print(f"Evaluating {len(examples)} examples...")

    # Run evaluation
    await orchestrator.run(examples)

    print(f"\nResults saved to {config.evaluation_exporter.output_path}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

!!! tip "Evaluation Tips"
    - **Use multiple metrics** - Different metrics capture different aspects of quality
    - **Track metrics over time** - Save results to monitor improvements
    - **Stratify your test set** - Include edge cases and representative samples
    - **Validate ground truth** - Errors in ground truth corrupt your metrics
