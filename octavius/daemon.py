"""Entrypoint: start the host bus on http://127.0.0.1:7777."""
from __future__ import annotations

import uvicorn

from .bus import bus
from .capabilities import register_all
from .config import HOST, PORT
from .web import create_app


def main() -> None:
    register_all(bus)
    app = create_app()
    print(f"Octavius host bus listening on http://{HOST}:{PORT}")
    print(f"  UI    →  http://{HOST}:{PORT}/")
    print(f"  MCP   →  http://{HOST}:{PORT}/mcp")
    print(f"  Caps  →  {', '.join(bus.capabilities())}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
