"""Abstract Base Class for File Listers.

This module defines the interface that all file lister implementations must satisfy.
File Listers are responsible for scanning a source
and returning a list of standardized identifiers to be processed.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseFileLister(ABC):
    """Abstract interface for file discovery."""

    @abstractmethod
    def list_files(self) -> list[PathIdentifier]:
        """Scans the target source and returns a list of file identifiers.

        This method should handle the logic to return a clean list of work items.

        Returns:
            List[PathIdentifier]: A list of standardized objects containing the
                                  path and any necessary execution context.
        """
        pass
