"""Base class shared by every specialist agent.

An agent is a role-specific system prompt plus a knowledge topic. Its system
prompt is assembled from three layers: the persona, the relevant slice of the
bundled knowledge base, and the **lessons learned** from past runs (memory) for
this role — so every generation benefits from prior reviews and feedback.
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from ..codegen import PROTOCOL, parse_files
from ..knowledge import context_for
from ..llm import LLM
from ..memory import Memory
from ..models import GeneratedFile

T = TypeVar("T", bound=BaseModel)


class Agent:
    """A single role in the pipeline (design, engineering, QA, ...)."""

    #: Short human-readable name, used in CLI output.
    name: str = "agent"
    #: Memory scope for lessons learned (see ``robloxforge.memory.ROLE_SCOPES``).
    role: str = "global"
    #: Knowledge topic to inject (see ``robloxforge.knowledge.TOPICS``).
    topic: str = ""
    #: The persona / instructions for this role.
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, llm: LLM, memory: Memory | None = None) -> None:
        self.llm = llm
        self.memory = memory

    def _system(self, *, genre: str | None = None) -> str:
        parts = [self.system_prompt]
        ctx = context_for(self.topic)
        if ctx:
            parts.append(ctx)
        if self.memory:
            lessons = self.memory.context_for(self.role, genre=genre)
            if lessons:
                parts.append(lessons)
        return "\n\n".join(parts)

    def ask_text(self, prompt: str, *, max_tokens: int = 32_000, genre: str | None = None) -> str:
        return self.llm.generate(system=self._system(genre=genre), prompt=prompt, max_tokens=max_tokens)

    def ask_model(
        self,
        prompt: str,
        model_cls: type[T],
        *,
        max_tokens: int = 16_000,
        genre: str | None = None,
    ) -> T:
        return self.llm.parse(
            system=self._system(genre=genre),
            prompt=prompt,
            model_cls=model_cls,
            max_tokens=max_tokens,
        )

    def ask_files(
        self, prompt: str, *, max_tokens: int = 48_000, genre: str | None = None
    ) -> list[GeneratedFile]:
        """Generate a batch of source files using the delimiter protocol."""
        text = self.ask_text(f"{prompt}\n\n{PROTOCOL}", max_tokens=max_tokens, genre=genre)
        return parse_files(text)
