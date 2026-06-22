"""A tiny file-delimiter protocol for getting many source files out of one call.

Asking the model to emit a JSON array of files forces every Luau file to be
JSON-escaped, which burns tokens and invites escaping bugs. Instead we ask for a
plain-text stream of delimited blocks and parse them here.

Block format::

    >>> FILE: ServerScriptService/Systems/Economy.luau
    >>> PURPOSE: Server-authoritative currency: grants, spends, leaderstats sync.
    <full luau source>
    >>> ENDFILE
"""

from __future__ import annotations

import re

from .models import GeneratedFile

_FILE_RE = re.compile(
    r">>>\s*FILE:\s*(?P<path>.+?)\s*\n"
    r"(?:>>>\s*PURPOSE:\s*(?P<purpose>.+?)\s*\n)?"
    r"(?P<body>.*?)"
    r">>>\s*ENDFILE",
    re.DOTALL,
)

#: Reusable instruction block describing the protocol to the model.
PROTOCOL = (
    "Output ONLY files using this exact delimited format, nothing else:\n"
    ">>> FILE: <path relative to src/>\n"
    ">>> PURPOSE: <one line>\n"
    "<full file source>\n"
    ">>> ENDFILE\n\n"
    "Repeat the block for each file. Do not wrap files in markdown code fences. "
    "Do not add commentary before, between, or after the blocks."
)


def parse_files(text: str) -> list[GeneratedFile]:
    """Parse a delimited code stream into :class:`GeneratedFile` objects."""
    files: list[GeneratedFile] = []
    for m in _FILE_RE.finditer(text):
        path = m.group("path").strip()
        body = m.group("body").strip("\n")
        # Defensively strip any stray code fences the model may have added.
        body = re.sub(r"^```[a-zA-Z]*\n", "", body)
        body = re.sub(r"\n```$", "", body)
        files.append(
            GeneratedFile(
                path=path,
                purpose=(m.group("purpose") or "").strip(),
                content=body,
            )
        )
    return files
