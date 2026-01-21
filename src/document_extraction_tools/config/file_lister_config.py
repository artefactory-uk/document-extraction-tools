"""Configuration for File Lister components."""

from typing import ClassVar

from pydantic import BaseModel


class BaseFileListerConfig(BaseModel):
    """Base config for File Listers.

    Implementations should subclass this to add specific parameters.
    """

    filename: ClassVar[str] = "file_lister.yaml"
