"""UI/UX agent: builds the game's interface as Luau-constructed ScreenGuis."""

from __future__ import annotations

from ..models import GameDesignDocument, GeneratedFile
from .base import Agent

_SYSTEM = """\
You are a Roblox UI/UX engineer who designs for engagement and mobile-first \
players (most Roblox sessions are on phones). You build interfaces in Luau by \
constructing Instances at runtime from client modules (no .rbxmx needed), using \
UIListLayout / UIGridLayout / UIAspectRatioConstraint / UIPadding / UICorner for \
responsive, touch-friendly layouts with large tap targets. You apply clear \
visual hierarchy, readable contrast, juicy feedback (tweens on press), and a HUD \
that surfaces currency, progression, and the next goal at all times. You wire \
buttons to the shared remotes the engineering stage defined.

Output Luau into the client/ tree (paths relative to src/), e.g. \
client/UI/Hud.luau and client/UI/Shop.luau, plus a client/UI/init.client.luau \
that mounts them. `Name.luau` = ModuleScript, `Name.client.luau` = LocalScript.\
"""


class UIUXAgent(Agent):
    name = "UI/UX"
    topic = "engineering"
    system_prompt = _SYSTEM

    def run(self, gdd: GameDesignDocument) -> list[GeneratedFile]:
        screens = "\n".join(f"- {s}" for s in gdd.ui_screens) or "- HUD\n- Shop"
        prompt = (
            "Build the UI for this game as Luau-constructed ScreenGuis. Implement "
            "each screen below plus an always-on HUD (currency, progression, "
            "current objective). Make it mobile-first and responsive, with tweened "
            "button feedback. Mount everything from a single "
            "client/UI/init.client.luau. Talk to the server only via the shared "
            "Remotes module.\n\n"
            f"SCREENS:\n{screens}\n\n"
            f"GAME DESIGN DOCUMENT:\n{gdd.model_dump_json(indent=2)}"
        )
        return self.ask_files(prompt, max_tokens=48_000)
