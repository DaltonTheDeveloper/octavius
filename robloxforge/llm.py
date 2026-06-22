"""Thin, opinionated wrapper around the Claude API for the pipeline.

Centralising the SDK usage means every agent automatically gets the right model,
adaptive thinking, streaming (so large code/design generations don't trip HTTP
timeouts), and structured-output handling. Agents never touch the SDK directly.

Two output shapes are supported, chosen by what fits the task:

* :meth:`generate` — free-form streamed text. Used for code generation, where
  output is large and JSON-escaping every Luau file would be wasteful.
* :meth:`parse` — a Pydantic model validated via structured outputs. Used for the
  smaller planning artifacts (market report, GDD, launch plan) where a strict
  schema is worth having.
"""

from __future__ import annotations

from typing import TypeVar

import anthropic
from pydantic import BaseModel

from .config import DEFAULT_EFFORT, DEFAULT_MODEL

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when the model can't be reached or returns something unusable."""


class LLM:
    """A small facade over ``anthropic.Anthropic`` tuned for RobloxForge."""

    def __init__(self, model: str = DEFAULT_MODEL, effort: str = DEFAULT_EFFORT) -> None:
        self.model = model
        self.effort = effort
        try:
            # Resolves credentials from ANTHROPIC_API_KEY (or an `ant` profile).
            self._client = anthropic.Anthropic()
        except Exception as exc:  # pragma: no cover - depends on env
            raise LLMError(
                "Could not initialise the Anthropic client. Set ANTHROPIC_API_KEY "
                "(get one at https://console.anthropic.com)."
            ) from exc

    # ------------------------------------------------------------------ text
    def generate(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = 32_000,
        effort: str | None = None,
    ) -> str:
        """Return the model's streamed text response to ``prompt``."""
        try:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                thinking={"type": "adaptive"},
                output_config={"effort": effort or self.effort},
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                message = stream.get_final_message()
        except anthropic.APIError as exc:
            raise LLMError(f"Claude API call failed: {exc}") from exc

        if message.stop_reason == "refusal":
            raise LLMError("Model declined this request.")
        text = "".join(b.text for b in message.content if b.type == "text").strip()
        if not text:
            raise LLMError("Model returned no text content.")
        return text

    # ----------------------------------------------------------------- model
    def parse(
        self,
        *,
        system: str,
        prompt: str,
        model_cls: type[T],
        max_tokens: int = 16_000,
        effort: str | None = None,
    ) -> T:
        """Return a validated instance of ``model_cls`` via structured outputs.

        ``messages.parse`` handles schema generation, stripping unsupported
        JSON-schema constraints, and validation for us.
        """
        # `messages.parse` populates output_config.format from `output_format`.
        # We deliberately don't pass our own output_config here to avoid any
        # chance of clobbering the SDK-managed format; effort defaults to the
        # model's standard depth, with adaptive thinking still on. (`effort` is
        # accepted for interface symmetry with generate().)
        _ = effort
        try:
            response = self._client.messages.parse(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                thinking={"type": "adaptive"},
                output_format=model_cls,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            raise LLMError(f"Claude API call failed: {exc}") from exc

        if response.stop_reason == "refusal":
            raise LLMError("Model declined this request.")
        parsed = response.parsed_output
        if parsed is None:
            raise LLMError("Model did not return a parseable structured result.")
        return parsed
