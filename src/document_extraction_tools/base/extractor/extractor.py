"""Abstract Base Class for Information Extractors.

This module defines the interface that all extractor implementations must satisfy.
Extractors are responsible for analyzing the structured Document
and populating a target Pydantic schema with specific data points.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from document_extraction_tools.types.document import Document

T = TypeVar("T", bound=BaseModel)


class BaseExtractor(ABC):
    """Abstract interface for data extraction."""

    @abstractmethod
    async def extract(self, document: Document, schema: type[T]) -> T:
        """Extracts structured data from a Document to match the provided Schema.

        This is an asynchronous operation to support I/O-bound tasks.

        Args:
            document (Document): The fully parsed document.
            schema (Type[T]): The Pydantic model class defining the target structure.

        Returns:
            T: An instance of the schema populated with the extracted data.
        """
        pass
