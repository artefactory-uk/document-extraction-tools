"""Configuration for the example file lister."""

from pydantic import Field

from document_extraction_tools.config.file_lister_config import BaseFileListerConfig


class FileListerConfig(BaseFileListerConfig):
    """Configuration for file listing."""

    source_dir: str = Field(..., description="Directory to scan for input files.")
    extensions: list[str] = Field(
        default_factory=lambda: [".pdf"],
        description="File extensions to include.",
    )
