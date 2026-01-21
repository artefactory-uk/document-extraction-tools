"""Local file reader implementation for the example pipeline."""

from pathlib import Path

from document_extraction_tools.base.reader.reader import BaseReader
from document_extraction_tools.examples.simple_lease_extraction.config.reader_config import (
    ReaderConfig,
)
from document_extraction_tools.types.document_bytes import DocumentBytes
from document_extraction_tools.types.path_identifier import PathIdentifier


class LocalFileReader(BaseReader):
    """Reads document bytes from local disk."""

    def __init__(self, config: ReaderConfig) -> None:
        """Initialize the reader with example config."""
        super().__init__(config)

    def read(self, path: PathIdentifier) -> DocumentBytes:
        """Read bytes from the given path identifier."""
        file_path = path.path if isinstance(path.path, Path) else Path(path.path)

        return DocumentBytes(
            file_bytes=file_path.read_bytes(),
            filename=file_path.name,
            original_source=str(file_path.absolute()),
            mime_type=self.config.mime_type,
        )
