"""Abstract Base Class for Data Exporters.

This module defines the interface that all exporter implementations must satisfy.
Exporters are responsible for taking the extracted, structured Pydantic data
and persisting it to a target destination.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.schema import ExtractionSchema


class BaseExtractionExporter(ABC):
    """Abstract interface for data persistence."""

    def __init__(self, config: BaseExtractionExporterConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseExtractionExporterConfig): Configuration specific to the exporter implementation.
        """
        self.config = config

    @abstractmethod
    async def export(self, document: Document, data: ExtractionSchema) -> None:
        """Persists extracted data to the configured destination.

        This is an asynchronous operation to support non-blocking I/O writes.

        Args:
            document (Document): The source document for this extraction.
            data (ExtractionSchema): The populated Pydantic model containing the extracted information.

        Returns:
            None: The method should raise an exception if the export fails.
        """
        pass
