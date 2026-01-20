"""Master Pipeline Configuration."""

from pydantic import BaseModel

from document_extraction_tools.config.converter_config import ConverterConfig
from document_extraction_tools.config.exporter_config import ExporterConfig
from document_extraction_tools.config.extractor_config import ExtractorConfig
from document_extraction_tools.config.file_lister_config import FileListerConfig
from document_extraction_tools.config.orchestrator_config import OrchestratorConfig
from document_extraction_tools.config.reader_config import ReaderConfig


class PipelineConfig(BaseModel):
    """Master container for component configurations.

    This class aggregates the configurations for all pipeline components.
    """

    orchestrator: OrchestratorConfig
    file_lister: FileListerConfig
    reader: ReaderConfig
    converter: ConverterConfig
    extractor: ExtractorConfig
    exporter: ExporterConfig
