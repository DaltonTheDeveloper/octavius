"""Luau engineering agent: implements the GDD's systems as a Rojo source tree."""

from __future__ import annotations

from ..models import GameDesignDocument, GeneratedFile
from .base import Agent

_SYSTEM = """\
You are an expert Roblox engineer who writes clean, idiomatic, strictly-typed \
Luau (--!strict). You build server-authoritative systems: never trust the \
client, validate every RemoteEvent/RemoteFunction argument, and keep currency \
and progression logic on the server. You use ModuleScripts for shared logic, a \
clear client/server split, and DataStore (with retry + session safety) for \
persistence. Your code is organised for a Rojo project with this layout, where \
paths are relative to src/:

  shared/   -> ReplicatedStorage.Shared   (ModuleScripts: config, types, remotes)
  server/   -> ServerScriptService.Server (*.server.luau Scripts + modules)
  client/   -> StarterPlayer.StarterPlayerScripts.Client (*.client.luau + modules)

File naming (Rojo): `Name.luau` = ModuleScript, `Name.server.luau` = Script, \
`Name.client.luau` = LocalScript. Define RemoteEvents/RemoteFunctions in a \
shared module that creates them on the server and waits for them on the client. \
Write real, working code — no TODO stubs for core systems.\
"""


class LuauEngineerAgent(Agent):
    name = "Luau Engineering"
    role = "engineering"
    topic = "engineering"
    system_prompt = _SYSTEM

    def run(self, gdd: GameDesignDocument) -> list[GeneratedFile]:
        prompt = (
            "Implement the MVP for this game as a complete Rojo source tree. "
            "Cover every system in mvp_scope with working, server-authoritative "
            "Luau. Include at minimum: a shared Config module, a shared Remotes "
            "module, a DataStore-backed persistence/profile module with retry, "
            "leaderstats setup, the core gameplay loop, the economy, and the "
            "monetization hooks (MarketplaceService for the listed passes/products). "
            "Wire client controllers that talk to the server only through the "
            "shared remotes. Keep it cohesive and runnable.\n\n"
            f"GAME DESIGN DOCUMENT:\n{gdd.model_dump_json(indent=2)}"
        )
        return self.ask_files(prompt, max_tokens=60_000)
