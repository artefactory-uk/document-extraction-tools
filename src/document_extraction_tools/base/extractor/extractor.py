"""Abstract Base Class for Information Extractors.

This module defines the interface that all extractor implementations must satisfy.
Extractors are responsible for analyzing the structured Document
and populating a target Pydantic schema with specific data points.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.schemas.schema import ExtractionSchema
from document_extraction_tools.types.document import Document


class BaseExtractor(ABC):
    """Abstract interface for data extraction."""

    @abstractmethod
    async def extract(
        self, document: Document, schema: type[ExtractionSchema]
    ) -> ExtractionSchema:
        """Extracts structured data from a Document to match the provided Schema.

        This is an asynchronous operation to support I/O-bound tasks.

        Args:
            document (Document): The fully parsed document.
            schema (type[ExtractionSchema]): The Pydantic model class defining the target structure.

        Returns:
            ExtractionSchema: An instance of the schema populated with the extracted data.
        """
        pass
