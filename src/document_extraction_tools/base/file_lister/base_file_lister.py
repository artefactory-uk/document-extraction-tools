"""Abstract Base Class for File Listers.

This module defines the interface that all file lister implementations must satisfy.
File Listers are responsible for scanning a source
and returning a list of standardized identifiers to be processed.
"""

from abc import ABC, abstractmethod

from document_extraction_tools.config.base_file_lister_config import (
    BaseFileListerConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.types.context import PipelineContext
from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseFileLister(ABC):
    """Abstract interface for file discovery.

    Attributes:
        config (BaseFileListerConfig): Component-specific configuration.
        pipeline_config (ExtractionPipelineConfig | None): Optional pipeline configuration
            when constructed with a pipeline config.
    """

    config: BaseFileListerConfig
    pipeline_config: ExtractionPipelineConfig | None

    def __init__(
        self,
        config: BaseFileListerConfig | ExtractionPipelineConfig,
    ) -> None:
        """Initialize with a configuration object.

        Args:
            config (BaseFileListerConfig | ExtractionPipelineConfig):
                Configuration specific to the file lister implementation or full pipeline configuration.
        """
        if isinstance(config, ExtractionPipelineConfig):
            self.pipeline_config = config
            self.config = config.file_lister
        else:
            self.pipeline_config = None
            self.config = config

    @abstractmethod
    def list_files(
        self, context: PipelineContext | None = None
    ) -> list[PathIdentifier]:
        """Scans the target source and returns a list of file identifiers.

        This method should handle the logic to return a clean list of work items.

        Args:
            context (PipelineContext | None): Optional shared pipeline context.

        Returns:
            List[PathIdentifier]: A list of standardized objects containing the
                                  path and any necessary execution context.
        """
        pass
