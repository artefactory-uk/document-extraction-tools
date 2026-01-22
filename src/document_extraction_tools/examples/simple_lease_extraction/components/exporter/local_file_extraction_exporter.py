"""Local file extraction exporter implementation for the example pipeline."""

from pathlib import Path

import aiofiles
from pydantic import BaseModel

from document_extraction_tools.base.exporter.extraction_exporter import (
    BaseExtractionExporter,
)
from document_extraction_tools.examples.simple_lease_extraction.config.extraction_exporter_config import (
    ExporterConfig,
)
from document_extraction_tools.types.document import Document


class LocalFileExtractionExporter(BaseExtractionExporter):
    """Writes extracted data to local JSON files."""

    def __init__(self, config: ExporterConfig) -> None:
        """Initialize exporter and ensure output directory exists."""
        super().__init__(config)
        Path(self.config.destination.path).mkdir(parents=True, exist_ok=True)

    async def export(self, document: Document, data: BaseModel) -> None:
        """Persist the extracted data as JSON."""
        filename = f"result_{document.id}"
        out_path = Path(self.config.destination.path) / f"{filename}.json"

        async with aiofiles.open(out_path, "w") as f:
            await f.write(data.model_dump_json(indent=2))
