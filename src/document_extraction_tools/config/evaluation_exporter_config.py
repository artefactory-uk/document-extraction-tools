"""Configuration for Evaluation Exporter components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseEvaluationExporterConfig(BaseModel):
    """Base config for Evaluation Exporters.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "evaluation_exporter.yaml"
