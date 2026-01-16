"""Master Pipeline Configuration."""

from pydantic import BaseModel

from document_extraction_tools.config.converter_config import BaseConverterConfig
from document_extraction_tools.config.exporter_config import BaseExporterConfig
from document_extraction_tools.config.extractor_config import BaseExtractorConfig
from document_extraction_tools.config.file_lister_config import BaseFileListerConfig
from document_extraction_tools.config.orchestrator_config import OrchestratorConfig
from document_extraction_tools.config.reader_config import BaseReaderConfig


class PipelineConfig(BaseModel):
    """Master container for component configurations.

    This class aggregates the configurations for all pipeline components.
    The specific types of the fields can be overridden at runtime by
    the config loader to support specific implementation configs.
    """

    orchestrator: OrchestratorConfig
    file_lister: BaseFileListerConfig
    reader: BaseReaderConfig
    converter: BaseConverterConfig
    extractor: BaseExtractorConfig
    exporter: BaseExporterConfig
