"""Field comparison helper used by example evaluators."""

import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

_MODEL_NAME = "gemini-3-flash-preview"
_PROMPT_TEMPLATE = """You are a judge for field-level equality.
Return whether the predicted value should be considered equal to the true value.
Respond with JSON only.

True value:
{true_value}

Predicted value:
{pred_value}
"""


class LlmJudgeResult(BaseModel):
    """Structured response for equality judgment."""

    is_equal: bool = Field(..., description="Whether the values are equivalent.")


def get_llm_judge_client() -> genai.Client:
    """Initialize and return a Gemini LLM client."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY in the environment.")
    return genai.Client(api_key=api_key)


def invoke_llm_as_a_judge(
    true_value: Any, pred_value: Any, client: genai.Client  # noqa: ANN401
) -> bool:
    """Return True when two field values should be considered equal."""
    prompt = _PROMPT_TEMPLATE.format(
        true_value=true_value,
        pred_value=pred_value,
    )

    response = client.models.generate_content(
        model=_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LlmJudgeResult,
        ),
    )

    return response.parsed.is_equal
