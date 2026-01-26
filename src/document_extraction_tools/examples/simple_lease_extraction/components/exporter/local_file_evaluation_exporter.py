"""Local file evaluation exporter for evaluation results."""

import json
from collections import defaultdict
from pathlib import Path

import aiofiles
import mlflow

from document_extraction_tools.base.exporter.base_evaluation_exporter import (
    BaseEvaluationExporter,
)
from document_extraction_tools.examples.simple_lease_extraction.config.local_file_evaluation_exporter_config import (
    LocalFileEvaluationExporterConfig,
)
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.evaluation_result import EvaluationResult


class LocalFileEvaluationExporter(BaseEvaluationExporter):
    """Writes evaluation results to local JSON files and logs metrics to MLflow."""

    def __init__(self, config: LocalFileEvaluationExporterConfig) -> None:
        """Initialize the local file evaluation exporter."""
        super().__init__(config)
        Path(self.config.destination.path).mkdir(parents=True, exist_ok=True)

    @mlflow.trace(name="export_evaluation_results", span_type="MEMORY")
    async def export(
        self, results: list[tuple[Document, list[EvaluationResult]]]
    ) -> None:
        """Export results to JSON files and log averages to MLflow."""
        span = mlflow.get_current_active_span()
        if span:
            span.set_inputs(
                {
                    "document_ids": [doc.id for doc, _ in results],
                    "results": [
                        [res.model_dump() for res in res_list]
                        for _, res_list in results
                    ],
                }
            )

        grouped_results = defaultdict(list)
        metric_values = defaultdict(list)

        for document, results_list in results:
            for result in results_list:
                metric_values[result.name].append(result.result)

                grouped_results[result.name].append(
                    {
                        "document_id": document.id,
                        "score": result.result,
                        "description": result.description,
                    }
                )

        for metric_name, values in metric_values.items():
            if values:
                avg_value = sum(values) / len(values)
                mlflow.log_metric(f"avg_{metric_name}", avg_value)

        for metric_name, entries in grouped_results.items():
            filename = f"{metric_name}.json"
            out_path = Path(self.config.destination.path) / filename

            async with aiofiles.open(out_path, "w") as f:
                await f.write(json.dumps(entries, indent=2))
