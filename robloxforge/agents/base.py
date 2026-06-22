"""Base class shared by every specialist agent.

An agent is a role-specific system prompt plus a knowledge topic. It delegates
the actual model call to the shared :class:`~robloxforge.llm.LLM` facade and
automatically prepends the relevant knowledge-base context.
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from ..codegen import PROTOCOL, parse_files
from ..knowledge import context_for
from ..llm import LLM
from ..models import GeneratedFile

T = TypeVar("T", bound=BaseModel)


class Agent:
    """A single role in the pipeline (design, engineering, QA, ...)."""

    #: Short human-readable name, used in CLI output.
    name: str = "agent"
    #: Knowledge topic to inject (see ``robloxforge.knowledge.TOPICS``).
    topic: str = ""
    #: The persona / instructions for this role.
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def _system(self) -> str:
        ctx = context_for(self.topic)
        return f"{self.system_prompt}\n\n{ctx}" if ctx else self.system_prompt

    def ask_text(self, prompt: str, *, max_tokens: int = 32_000, effort: str | None = None) -> str:
        return self.llm.generate(
            system=self._system(), prompt=prompt, max_tokens=max_tokens, effort=effort
        )

    def ask_model(
        self,
        prompt: str,
        model_cls: type[T],
        *,
        max_tokens: int = 16_000,
        effort: str | None = None,
    ) -> T:
        return self.llm.parse(
            system=self._system(),
            prompt=prompt,
            model_cls=model_cls,
            max_tokens=max_tokens,
            effort=effort,
        )

    def ask_files(
        self, prompt: str, *, max_tokens: int = 48_000, effort: str | None = None
    ) -> list[GeneratedFile]:
        """Generate a batch of source files using the delimiter protocol."""
        text = self.ask_text(f"{prompt}\n\n{PROTOCOL}", max_tokens=max_tokens, effort=effort)
        return parse_files(text)
