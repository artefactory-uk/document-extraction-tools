"""Abstract Base Class for Data Exporters.

This module defines the interface that all exporter implementations must satisfy.
Exporters are responsible for taking the extracted, structured Pydantic data
and persisting it to a target destination.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.schemas.schema import ExtractionSchema
from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseExporter(ABC):
    """Abstract interface for data persistence."""

    def __init__(self, destination: PathIdentifier) -> None:
        """Initializes the exporter with a fixed destination.

        Args:
            destination (PathIdentifier): The target root location.
        """
        self.destination = destination

    @abstractmethod
    async def export(self, data: ExtractionSchema) -> None:
        """Persists extracted data to the configured destination.

        This is an asynchronous operation to support non-blocking I/O writes.

        Args:
            data (ExtractionSchema): The populated Pydantic model containing the extracted information.

        Returns:
            None: The method should raise an exception if the export fails.
        """
        pass
