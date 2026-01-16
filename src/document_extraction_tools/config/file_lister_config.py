"""Base configuration for File Lister components."""

from pydantic import BaseModel


class BaseFileListerConfig(BaseModel):
    """Base config for File Listers.

    Implementations should subclass this to add specific parameters.
    """

    pass
