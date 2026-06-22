"""Writes a generated game out as a ready-to-open Rojo project on disk."""

from __future__ import annotations

import re
from pathlib import Path

from ..models import GeneratedFile
from . import templates


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return slug or "roblox-game"


def _safe_join(root: Path, rel: str) -> Path:
    """Resolve ``rel`` under ``root``, refusing paths that escape the tree."""
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"Refusing to write outside project: {rel}")
    return target


def scaffold_project(
    name: str,
    pitch: str,
    files: list[GeneratedFile],
    dest: Path,
) -> Path:
    """Create a complete Rojo project for ``name`` at ``dest`` and return its path.

    Writes every generated ``src/`` file plus the toolchain/config files that
    make the project open in Studio and lint with the standard tools.
    """
    project_dir = dest / _slug(name)
    src = project_dir / "src"
    for sub in ("shared", "server", "client"):
        (src / sub).mkdir(parents=True, exist_ok=True)

    for f in files:
        rel = f.path
        # The model is told paths are relative to src/; tolerate a leading "src/".
        if rel.startswith("src/"):
            rel = rel[len("src/") :]
        path = _safe_join(src, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f.content, encoding="utf-8")

    # Toolchain + Rojo config.
    (project_dir / "default.project.json").write_text(
        templates.default_project_json(name), encoding="utf-8"
    )
    (project_dir / "rokit.toml").write_text(templates.ROKIT_TOML, encoding="utf-8")
    (project_dir / "wally.toml").write_text(templates.WALLY_TOML, encoding="utf-8")
    (project_dir / "selene.toml").write_text(templates.SELENE_TOML, encoding="utf-8")
    (project_dir / ".luaurc").write_text(templates.LUAURC, encoding="utf-8")
    (project_dir / "README.md").write_text(templates.game_readme(name, pitch), encoding="utf-8")

    return project_dir
