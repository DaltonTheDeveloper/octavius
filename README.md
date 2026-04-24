# Octavius

Local host bus that gives Claude (via Claude Code, no API key) **structured access to your whole machine** — not screenshots, not a sandbox. Every risky action is queued for one-click approval in a sidebar UI, and every committed action is reversible from a journal.

## Why this exists

Two ruts everyone else is in:
- **Pixel puppets** (computer-use): universal but slow and brittle.
- **Per-app MCP servers**: reliable but siloed — Claude can't reason across apps.

Octavius is the third path: a **graph of your machine** + a **capability registry** + a **journal** with one-key undo + an **approval UI**. Claude reasons across apps, you stay in control.

## What's in the box

```
octavius/
├── daemon.py         # one process, port 7777
├── graph.py          # processes, volumes, UE5 projects, Chrome state
├── journal.py        # append-only with inverse ops + undo
├── bus.py            # pending-action queue + SSE
├── mcp_server.py     # MCP tools exposed to Claude Code
├── web.py            # FastAPI: /mcp + / + /api/*
├── ui/index.html     # sidebar with approve/reject buttons
└── capabilities/
    ├── shell.py      # shell.run
    ├── filesystem.py # fs.move, fs.copy, fs.write, fs.delete (all journaled)
    ├── ue5.py        # ue5.move_project, ue5.read_uproject, ue5.launch_editor
    └── chrome.py     # chrome.open_url, chrome.list_tabs, chrome.run_js
```

## Install

```sh
./scripts/install.sh
source .venv/bin/activate
octavius-bus
```

Open the sidebar UI at http://127.0.0.1:7777/

In another terminal:

```sh
claude mcp add --transport http octavius http://127.0.0.1:7777/mcp
```

## What Claude can do now

In Claude Code, try:

> Show me the live machine graph and tell me what UE5 projects you can see.

> I want to move my UE5 project `MyGame` to my external drive at `/Volumes/Backup`. Propose the action — I'll approve it in the UI.

> Open `https://docs.unrealengine.com` in a new Chrome tab, then list all my open tabs.

Every action that mutates state shows up as a button in the sidebar. Click **Approve** and Claude continues; click **Reject** and Claude gets told no.

## Undo

Every committed action records an inverse. Click **Undo last action** in the sidebar, or ask Claude:

> Undo the last 3 actions.

Filesystem ops have real inverses; shell/browse ops are forward-only and skipped.

## Adding a capability

A capability is just an async function `(params: dict) -> dict` registered with the bus. To add one for, say, Blender:

```python
# octavius/capabilities/blender.py
from .. import journal

async def _open_file(params):
    # ... do the thing
    journal.record(kind="blender.open", forward=params, inverse=None)
    return {"opened": params["path"]}

def register(bus):
    bus.register("blender.open_file", _open_file)
```

Then add `register_blender(bus)` in `capabilities/__init__.py`. Claude immediately sees it via `list_capabilities`.

## What this is NOT (yet)

- A marketplace. That's the next layer — package capabilities as installable bundles, sign them, host an index.
- A recorder. The "intent-replay" idea (record your interactions, generalize them) lives in a follow-up branch.
- Cross-platform. macOS-first; Chrome capability uses AppleScript. Windows/Linux equivalents are straightforward swaps.

## Roadmap

1. **Recorder** — capture user input traces and turn them into reusable capabilities (the marketplace primitive).
2. **Capability bundles** — `octavius install <name>` pulling from a registry, with manifests + signatures.
3. **Cross-app capabilities** — abstract verbs like `move_with_dependencies` that dispatch to whichever app provider can handle them.
4. **Voice/Raycast clients** — host bus is just a socket; nothing prevents other front-ends sharing the same graph + journal.
