"""Common schema definitions and type variables."""

from typing import TypeVar

from pydantic import BaseModel

ExtractionSchema = TypeVar("ExtractionSchema", bound=BaseModel)
