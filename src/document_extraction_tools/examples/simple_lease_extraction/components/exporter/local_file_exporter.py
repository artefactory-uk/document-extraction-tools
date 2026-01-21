"""JSON exporter implementation for the example pipeline."""

from pathlib import Path

import aiofiles
from pydantic import BaseModel

from document_extraction_tools.base.exporter.exporter import BaseExporter
from document_extraction_tools.examples.simple_lease_extraction.config.exporter_config import (
    ExporterConfig,
)


class LocalFileExporter(BaseExporter):
    """Writes extracted data to local JSON files."""

    def __init__(self, config: ExporterConfig) -> None:
        """Initialize exporter and ensure output directory exists."""
        super().__init__(config)
        Path(self.config.destination.path).mkdir(parents=True, exist_ok=True)

    async def export(self, data: BaseModel) -> None:
        """Persist the extracted data as JSON."""
        filename = f"lease_result_{id(data)}"
        out_path = Path(self.config.destination.path) / f"{filename}.json"

        async with aiofiles.open(out_path, "w") as f:
            await f.write(data.model_dump_json(indent=2))
