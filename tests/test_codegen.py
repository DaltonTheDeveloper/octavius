"""Offline tests for the code-generation protocol and Rojo scaffolding.

These don't touch the Claude API — they exercise the deterministic plumbing.
"""

from __future__ import annotations

import pytest

from robloxforge.codegen import parse_files
from robloxforge.models import GeneratedFile
from robloxforge.roblox.rojo import _safe_join, scaffold_project


def test_parse_files_extracts_blocks():
    text = (
        ">>> FILE: shared/Config.luau\n"
        ">>> PURPOSE: tunables\n"
        "return { Coins = 0 }\n"
        ">>> ENDFILE\n"
        ">>> FILE: server/Main.server.luau\n"
        "print('hi')\n"
        ">>> ENDFILE\n"
    )
    files = parse_files(text)
    assert [f.path for f in files] == ["shared/Config.luau", "server/Main.server.luau"]
    assert files[0].purpose == "tunables"
    assert "return { Coins = 0 }" in files[0].content


def test_parse_files_strips_code_fences():
    text = ">>> FILE: a.luau\n```lua\nlocal x = 1\n```\n>>> ENDFILE\n"
    files = parse_files(text)
    assert files[0].content == "local x = 1"


def test_safe_join_rejects_escape(tmp_path):
    with pytest.raises(ValueError):
        _safe_join(tmp_path, "../../etc/passwd")


def test_scaffold_writes_project(tmp_path):
    files = [
        GeneratedFile(path="shared/Config.luau", purpose="cfg", content="return {}"),
        GeneratedFile(path="server/Main.server.luau", purpose="main", content="print(1)"),
    ]
    project = scaffold_project("My Cool Game", "A pitch.", files, tmp_path)
    assert (project / "default.project.json").exists()
    assert (project / "rokit.toml").exists()
    assert (project / "src" / "shared" / "Config.luau").read_text() == "return {}"
    assert (project / "src" / "server" / "Main.server.luau").exists()
    assert project.name == "my-cool-game"
