"""Model backends — where completions actually come from.

RobloxForge defaults to driving **Claude Code** (the `claude` CLI in headless
print mode), so it runs on your Claude subscription with **no API key and no
per-token billing**. An Anthropic-API backend is available as an opt-in for
unattended/CI use (`FORGE_BACKEND=api`).

Both backends implement the same tiny contract: ``complete(system, prompt) ->
str``. Everything higher up (structured parsing, the file protocol, agents) is
backend-agnostic.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from typing import Protocol


class BackendError(RuntimeError):
    """Raised when a backend can't produce a completion."""


class Backend(Protocol):
    """Anything that can turn a (system, prompt) pair into text."""

    name: str

    def complete(self, *, system: str, prompt: str, max_tokens: int = 32_000) -> str: ...


class ClaudeCodeBackend:
    """Runs completions through the local ``claude`` CLI (no API key).

    Each call spawns ``claude -p`` with our persona as the system prompt, tools
    disabled (we only want text — never file/bash side effects), and JSON output
    so we can reliably extract the result. Runs in a temp cwd so the host repo's
    ``CLAUDE.md`` / project settings don't bleed into generations.
    """

    name = "claude-code"

    def __init__(self, model: str, effort: str = "high", *, timeout: float = 900.0) -> None:
        self.model = model
        self.effort = effort
        self.timeout = timeout
        self._bin = shutil.which("claude")
        if not self._bin:
            raise BackendError(
                "The `claude` CLI was not found on PATH. Install Claude Code "
                "(https://docs.claude.com/en/docs/claude-code) and run `claude` "
                "once to authenticate, or set FORGE_BACKEND=api."
            )

    def complete(self, *, system: str, prompt: str, max_tokens: int = 32_000) -> str:
        cmd = [
            self._bin,
            "-p",
            "--output-format", "json",
            "--model", self.model,
            "--effort", self.effort,
            "--tools", "",                 # text only; no Edit/Bash/etc.
            "--no-session-persistence",    # don't litter session files
        ]
        if system:
            cmd += ["--system-prompt", system]
        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=tempfile.gettempdir(),  # neutral cwd → no CLAUDE.md pickup
            )
        except subprocess.TimeoutExpired as exc:
            raise BackendError(f"claude CLI timed out after {self.timeout}s") from exc

        if proc.returncode != 0:
            raise BackendError(
                f"claude CLI exited {proc.returncode}: {(proc.stderr or proc.stdout)[:500]}"
            )
        return self._extract(proc.stdout)

    @staticmethod
    def _extract(stdout: str) -> str:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            # Older/edge formats may already be plain text.
            text = stdout.strip()
            if text:
                return text
            raise BackendError("claude CLI returned no parseable output.") from None
        if isinstance(payload, dict):
            if payload.get("is_error"):
                raise BackendError(f"claude CLI error: {payload.get('result', payload)}")
            result = payload.get("result")
            if isinstance(result, str) and result.strip():
                return result.strip()
        raise BackendError(f"claude CLI returned an unexpected payload: {str(payload)[:300]}")


class AnthropicBackend:
    """Runs completions through the Anthropic API (opt-in; needs ANTHROPIC_API_KEY)."""

    name = "api"

    def __init__(self, model: str, effort: str = "high") -> None:
        try:
            import anthropic  # imported lazily so it's an optional dependency
        except ImportError as exc:  # pragma: no cover
            raise BackendError(
                "The Anthropic backend needs the `anthropic` package. "
                "Install it with: pip install 'robloxforge[api]'."
            ) from exc
        self._anthropic = anthropic
        self.model = model
        self.effort = effort
        try:
            self._client = anthropic.Anthropic()
        except Exception as exc:  # pragma: no cover - depends on env
            raise BackendError("Could not init Anthropic client (set ANTHROPIC_API_KEY).") from exc

    def complete(self, *, system: str, prompt: str, max_tokens: int = 32_000) -> str:
        try:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                thinking={"type": "adaptive"},
                output_config={"effort": self.effort},
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                message = stream.get_final_message()
        except self._anthropic.APIError as exc:
            raise BackendError(f"Anthropic API call failed: {exc}") from exc
        if message.stop_reason == "refusal":
            raise BackendError("Model declined this request.")
        text = "".join(b.text for b in message.content if b.type == "text").strip()
        if not text:
            raise BackendError("Model returned no text content.")
        return text


def make_backend(kind: str, model: str, effort: str) -> Backend:
    """Construct the configured backend (``claude-code`` or ``api``)."""
    kind = (kind or "claude-code").lower()
    if kind in ("claude-code", "claude", "cli", "cc"):
        return ClaudeCodeBackend(model=model, effort=effort)
    if kind in ("api", "anthropic"):
        return AnthropicBackend(model=model, effort=effort)
    raise BackendError(f"Unknown backend '{kind}'. Use 'claude-code' or 'api'.")
