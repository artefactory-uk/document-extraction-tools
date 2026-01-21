"""Abstract Base Class for Document Converters.

This module defines the interface that all converter implementations must satisfy.
Converters are responsible for transforming raw binary data (DocumentBytes)
into a structured Document object containing pages and content.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.converter_config import BaseConverterConfig
from document_extraction_tools.types.document import Document
from document_extraction_tools.types.document_bytes import DocumentBytes


class BaseConverter(ABC):
    """Abstract interface for document transformation."""

    def __init__(self, config: BaseConverterConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseConverterConfig): Configuration specific to the converter implementation.
        """
        self.config = config

    @abstractmethod
    def convert(self, document_bytes: DocumentBytes) -> Document:
        """Transforms raw document bytes into a structured Document object.

        This method should handle the parsing logic and map the metadata from the
        input bytes to the output document.

        Args:
            document_bytes (DocumentBytes): The standardized raw input containing
                                            file bytes and source metadata.

        Returns:
            Document: The fully structured document model ready for extraction.
        """
        pass
