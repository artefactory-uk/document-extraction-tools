"""Configuration for the local file reader."""

from pydantic import Field

from document_extraction_tools.config.base_reader_config import BaseReaderConfig


class LocalFileReaderConfig(BaseReaderConfig):
    """Configuration for local file reading."""

    mime_type: str = Field(
        default="application/pdf",
        description="MIME type to associate with read files.",
    )
