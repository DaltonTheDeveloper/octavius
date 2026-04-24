"""Binary analysis — Mach-O introspection for reverse engineering closed apps.

Pulls together the standard macOS reverse-engineering toolkit into one
structured report Claude can reason over. With this, Claude can look at
EGL's binary and learn class names, exported symbols, embedded URLs,
linked frameworks — enough to draft per-app capabilities for apps with
no AX, no scripting, no public API.

Output is JSON-friendly. Heavy operations are size-capped so we don't
return MBs of strings to the LLM.
"""
from __future__ import annotations

import asyncio
import re
import subprocess
from pathlib import Path
from typing import Any

from .. import journal


async def _sh(*cmd: str, timeout: int = 20) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", "timeout"
    return proc.returncode or 0, out.decode(errors="replace"), err.decode(errors="replace")


def _resolve_binary(path_input: str) -> Path:
    p = Path(path_input).expanduser().resolve()
    if p.suffix == ".app" or p.name.endswith(".app"):
        # Pull the main executable out of Contents/MacOS/
        macos = p / "Contents" / "MacOS"
        if macos.exists():
            execs = [f for f in macos.iterdir() if f.is_file() and f.stat().st_mode & 0o100]
            if execs:
                return execs[0]
    return p


async def _file_type(binary: Path) -> str:
    code, out, _ = await _sh("file", str(binary))
    return out.strip()


async def _otool_libs(binary: Path) -> list[str]:
    code, out, _ = await _sh("otool", "-L", str(binary), timeout=15)
    if code != 0:
        return []
    lines = out.splitlines()[1:]  # skip the "<path>:" header
    return [line.strip().split()[0] for line in lines if line.strip()][:200]


async def _otool_load_commands(binary: Path) -> dict[str, Any]:
    """Mach-O load commands — segments, libraries, entry point."""
    code, out, _ = await _sh("otool", "-l", str(binary), timeout=15)
    if code != 0:
        return {}
    commands: list[str] = []
    for m in re.finditer(r"cmd (LC_\w+)", out):
        commands.append(m.group(1))
    return {
        "command_count": len(commands),
        "command_summary": dict((c, commands.count(c)) for c in sorted(set(commands))),
    }


async def _objc_classes(binary: Path) -> list[str]:
    """Get Objective-C class names via otool -ov (verbose ObjC metadata)."""
    code, out, _ = await _sh("otool", "-ov", str(binary), timeout=30)
    if code != 0:
        return []
    classes = sorted(set(re.findall(r"name\s+0x[0-9a-f]+\s+(\w+)", out[:500_000])))
    # Filter for class-name-looking things (CamelCase with class hint)
    classes = [c for c in classes if c[0].isupper() and len(c) >= 4]
    return classes[:300]


async def _exported_symbols(binary: Path) -> list[str]:
    """Exported symbols via nm — useful for finding public C/C++ APIs."""
    code, out, _ = await _sh("nm", "-gU", str(binary), timeout=20)
    if code != 0:
        return []
    syms: list[str] = []
    for line in out.splitlines()[:5000]:
        parts = line.strip().split()
        if len(parts) >= 3:
            syms.append(parts[-1])
    return sorted(set(syms))[:500]


async def _entitlements(target: Path) -> dict[str, Any]:
    # codesign needs the .app bundle path, not the inner binary
    bundle = target
    while bundle != bundle.parent:
        if bundle.name.endswith(".app"):
            break
        bundle = bundle.parent
    code, out, _ = await _sh("codesign", "-d", "--entitlements", ":-", str(bundle), timeout=10)
    if code != 0 or not out.strip():
        return {}
    try:
        import plistlib
        return plistlib.loads(out.encode())
    except Exception:
        return {"_raw": out[:2000]}


async def _interesting_strings(binary: Path) -> dict[str, list[str]]:
    """Pull URLs / API endpoints / config keys / format strings from the binary."""
    code, out, _ = await _sh("strings", "-a", "-n", "8", str(binary), timeout=30)
    if code != 0:
        return {}
    text = out
    urls = sorted(set(re.findall(r"https?://[a-zA-Z0-9._/\-?=&%+]+", text)))[:80]
    api_paths = sorted(set(re.findall(r"/api/v?\d?/[a-zA-Z0-9_/\-]+", text)))[:80]
    bundle_ids = sorted(set(re.findall(r"\bcom\.[a-z][a-z0-9.\-]+", text)))[:80]
    selectors = sorted(set(re.findall(r"\b[a-z][a-zA-Z0-9]+:[a-zA-Z][a-zA-Z0-9:]+\b", text)))[:80]
    return {
        "urls": urls,
        "api_paths": api_paths,
        "bundle_ids_referenced": bundle_ids,
        "objc_selectors_sample": selectors,
    }


async def _class_dump(binary: Path) -> dict[str, Any]:
    """If class-dump is installed, get a richer ObjC interface dump."""
    import shutil as _shutil
    cd = _shutil.which("class-dump")
    if not cd:
        return {"available": False, "hint": "brew install class-dump"}
    code, out, _ = await _sh(cd, "-A", str(binary), timeout=60)
    if code != 0:
        return {"available": True, "error": "class-dump failed"}
    # extract @interface / @protocol blocks
    interfaces = re.findall(r"@interface\s+(\w+)(?::\s+(\w+))?", out)
    protocols = re.findall(r"@protocol\s+(\w+)", out)
    return {
        "available": True,
        "interface_count": len(interfaces),
        "protocol_count": len(set(protocols)),
        "interfaces_sample": [{"name": n, "super": s or None} for n, s in interfaces[:80]],
        "protocols_sample": sorted(set(protocols))[:80],
    }


async def _analyze(params: dict[str, Any]) -> dict[str, Any]:
    binary = _resolve_binary(params["path"])
    if not binary.exists():
        raise FileNotFoundError(binary)

    depth = params.get("depth", "deep")  # quick | deep
    coros = [
        _file_type(binary),
        _otool_libs(binary),
        _otool_load_commands(binary),
        _entitlements(binary),
    ]
    file_t, libs, lcs, ents = await asyncio.gather(*coros)

    report: dict[str, Any] = {
        "binary": str(binary),
        "file_type": file_t,
        "linked_libraries": libs,
        "linked_libraries_count": len(libs),
        "load_commands": lcs,
        "entitlements_keys": list(ents.keys()) if isinstance(ents, dict) else [],
    }

    if depth == "deep":
        deep_coros = [
            _objc_classes(binary),
            _exported_symbols(binary),
            _interesting_strings(binary),
            _class_dump(binary),
        ]
        classes, syms, strings, cdump = await asyncio.gather(*deep_coros)
        report.update({
            "objc_classes_sample": classes,
            "objc_class_count_sample": len(classes),
            "exported_symbols_sample": syms,
            "exported_symbol_count_sample": len(syms),
            "interesting_strings": strings,
            "class_dump": cdump,
        })

    journal.record(
        kind="binary.analyze",
        forward={"path": str(binary), "depth": depth},
        inverse=None,
    )
    return report


def register(bus) -> None:
    bus.register("binary.analyze", _analyze)
