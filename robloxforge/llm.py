"""The model facade the agents talk to.

It wraps a pluggable :class:`~robloxforge.backends.Backend` (Claude Code by
default, Anthropic API opt-in) and adds backend-agnostic structured parsing:

* :meth:`generate` — free-form text (Luau code, markdown).
* :meth:`parse` — a validated Pydantic model. Implemented on top of ``generate``
  by asking for JSON against the model's schema, then validating (with one
  corrective retry) — so it works identically on either backend.
"""

from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from .backends import Backend, BackendError, make_backend
from .config import DEFAULT_BACKEND, DEFAULT_EFFORT, DEFAULT_MODEL

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when the model can't be reached or returns something unusable."""


class LLM:
    """Backend-agnostic model facade used by every agent."""

    def __init__(
        self,
        *,
        backend: str = DEFAULT_BACKEND,
        model: str = DEFAULT_MODEL,
        effort: str = DEFAULT_EFFORT,
    ) -> None:
        self.model = model
        self.effort = effort
        try:
            self._backend: Backend = make_backend(backend, model, effort)
        except BackendError as exc:
            raise LLMError(str(exc)) from exc

    @property
    def backend_name(self) -> str:
        return self._backend.name

    # ------------------------------------------------------------------ text
    def generate(self, *, system: str, prompt: str, max_tokens: int = 32_000) -> str:
        try:
            return self._backend.complete(system=system, prompt=prompt, max_tokens=max_tokens)
        except BackendError as exc:
            raise LLMError(str(exc)) from exc

    # ----------------------------------------------------------------- model
    def parse(self, *, system: str, prompt: str, model_cls: type[T], max_tokens: int = 16_000) -> T:
        """Return a validated ``model_cls`` instance.

        Embeds the JSON schema in the prompt, extracts the JSON object from the
        reply, and validates it. On a validation/parse failure it retries once,
        feeding the error back so the model can correct itself.
        """
        schema = json.dumps(model_cls.model_json_schema(), indent=2)
        base = (
            f"{prompt}\n\n"
            "Respond with a SINGLE JSON object and nothing else (no prose, no "
            "markdown fences). It must validate against this JSON schema:\n"
            f"{schema}"
        )

        last_err = ""
        for attempt in range(2):
            ask = base if attempt == 0 else (
                f"{base}\n\nYour previous answer was invalid: {last_err}\n"
                "Return corrected JSON only."
            )
            text = self.generate(system=system, prompt=ask, max_tokens=max_tokens)
            try:
                data = _extract_json(text)
                return model_cls.model_validate(data)
            except (ValueError, ValidationError) as exc:
                last_err = str(exc)[:400]
        raise LLMError(f"Could not get valid {model_cls.__name__} JSON: {last_err}")


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model reply, tolerating fences/preamble."""
    text = text.strip()
    # Strip ```json fences if present.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost {...} span.
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("no JSON object found in reply")
