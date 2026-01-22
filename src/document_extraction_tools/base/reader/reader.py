"""Abstract Base Class for Document Readers.

This module defines the interface that all reader implementations must satisfy.
Readers are responsible for fetching raw file content from a source
and returning it as a standardized DocumentBytes object.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.reader_config import BaseReaderConfig
from document_extraction_tools.types.document_bytes import DocumentBytes
from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseReader(ABC):
    """Abstract interface for document ingestion."""

    def __init__(self, config: BaseReaderConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseReaderConfig): Configuration specific to the reader implementation.
        """
        self.config = config

    @abstractmethod
    def read(self, path_identifier: PathIdentifier) -> DocumentBytes:
        """Reads a document from a specific source and returns its raw bytes.

        Args:
            path_identifier (PathIdentifier): The identifier for the file.

        Returns:
            DocumentBytes: A standardized container with raw bytes and source metadata.
        """
        pass
