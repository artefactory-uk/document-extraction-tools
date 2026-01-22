"""Local file evaluation exporter for evaluation results."""

from pathlib import Path

import aiofiles

from document_extraction_tools.base.exporter.evaluation_exporter import (
    BaseEvaluationExporter,
)
from document_extraction_tools.examples.simple_lease_extraction.config.evaluation_exporter_config import (
    EvaluationExporterConfig,
)
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.evaluation_result import EvaluationResult


class LocalFileEvaluationExporter(BaseEvaluationExporter):
    """Writes evaluation results to a local JSON file."""

    def __init__(self, config: EvaluationExporterConfig) -> None:
        """Initialize the local file evaluation exporter."""
        super().__init__(config)
        Path(self.config.destination.path).mkdir(parents=True, exist_ok=True)

    async def export(self, document: Document, results: list[EvaluationResult]) -> None:
        """Export evaluation results to local JSON files."""
        for result in results:
            filename = f"{result.name}_{document.id}"
            out_path = Path(self.config.destination.path) / f"{filename}.json"

            async with aiofiles.open(out_path, "w") as f:
                await f.write(result.model_dump_json(indent=2))
