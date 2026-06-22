# 🎮 RobloxForge

**An AI pipeline that automates Roblox game development end-to-end** — market
research, game design, Luau engineering, UI/UX, QA, and a free-growth launch plan
— and hands you a ready-to-open [Rojo](https://rojo.space) project.

You give it an idea (or nothing). It researches what's trending, picks a concept
that can grow organically and monetize cleanly, writes a game design document,
generates server-authoritative Luau and a mobile-first UI, reviews the code for
exploits and data loss, writes tests, and produces a launch playbook for getting
your first players **for free**.

It is built on the [Claude API](https://docs.claude.com) (Opus 4.8) and grounded
in a researched [knowledge base](docs/) of how Roblox games are actually built,
shipped, and grown.

> **Honest framing:** no tool can *guarantee* a hit — Roblox earnings are
> extremely top-heavy (the median DevEx creator earns ~$1,575/yr). What
> RobloxForge does is automate the whole craft and bias every stage toward the
> two things that actually drive success: **per-user retention** and
> **organic discovery**. The rest is iteration, taste, and live-ops — which it
> also plans for you.

## How it works

```
brief ─▶ Market Research ─▶ Game Design ─▶ Engineering ─▶ UI/UX ─▶ QA ─▶ Marketing
          (06,05)            (04,05)         (01,04)        (01)     (qa)   (07,08)
                                                                              │
                                                                              ▼
                                                         a Rojo project + forge/ artifacts
```

Each stage is a specialist [agent](robloxforge/agents) with a role-specific
prompt, fed the relevant [`docs/`](docs/) as grounding context. Every stage's
output is a typed artifact consumed by the next. The result is written to disk as
a Rojo project (`src/shared`, `src/server`, `src/client`) plus a `forge/` folder
holding the market report, GDD, QA report, and launch plan.

## Install

```sh
pip install -e .            # or: pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-...   # https://console.anthropic.com
```

## Use

```sh
# Generate a complete game from an idea (or a vague direction)
forge new "a chill pet-collecting game with a steal-and-defend twist"

# Just see ranked, buildable concepts for an idea
forge research "horror co-op for mobile"

# Check your setup (model, keys, toolchain)
forge info

# Publish a built place to a live experience via Open Cloud (optional)
forge publish MyGame.rbxlx
```

`forge new` prints where the project landed. Open it in Studio:

```sh
cd games/<your-game>
rokit install          # installs Rojo, Selene, StyLua (pinned in rokit.toml)
rojo serve             # connect from the Rojo Studio plugin
```

The free-growth launch playbook is at `games/<your-game>/forge/LAUNCH.md`.

## What's in the box

```
robloxforge/
├── cli.py            # `forge` CLI (new / research / publish / info)
├── pipeline.py       # orchestrates the 6-stage pipeline
├── llm.py            # Claude API wrapper (adaptive thinking, streaming, JSON)
├── models.py         # typed artifacts (GDD, MarketReport, LaunchPlan, ...)
├── knowledge.py      # injects docs/ into each agent
├── codegen.py        # file-delimiter protocol for multi-file code generation
├── agents/           # market research, design, engineering, UI/UX, QA, marketing
└── roblox/
    ├── rojo.py       # scaffolds a ready-to-open Rojo project
    ├── opencloud.py  # Open Cloud client (publish, datastore, messaging, assets)
    └── templates.py  # default.project.json, rokit/wally/selene/.luaurc
docs/                 # the researched Roblox knowledge base (also great reading)
```

## Configuration

| Env var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Required. The Claude API key the pipeline runs on. |
| `FORGE_MODEL` | Model id (default `claude-opus-4-8`). |
| `FORGE_EFFORT` | `low`/`medium`/`high`/`max` (default `high`). |
| `FORGE_OUTPUT` | Output directory (default `games/`). |
| `ROBLOX_API_KEY` | Optional. [Open Cloud](docs/03-open-cloud-api.md) key for publishing. |
| `ROBLOX_UNIVERSE_ID` / `ROBLOX_PLACE_ID` | Optional. Target experience to publish to. |
| `ROBLOX_CREATOR_ID` / `ROBLOX_CREATOR_TYPE` | Optional. For asset uploads. |

## The knowledge base

The [`docs/`](docs/) folder is a researched field manual for shipping a hit
Roblox game (every claim is sourced):

- [00 — Overview](docs/00-overview.md)
- [01 — Luau, Studio & UI](docs/01-luau-and-studio.md)
- [02 — Tooling: Rojo, Wally, Selene, StyLua, TestEZ](docs/02-tooling-rojo-wally.md)
- [03 — Open Cloud API](docs/03-open-cloud-api.md)
- [04 — Core game systems & anti-exploit](docs/04-game-systems.md)
- [05 — Market trends & monetization](docs/05-market-and-monetization.md)
- [06 — The discovery algorithm](docs/06-discovery-algorithm.md) ← the most important one
- [07 — Free user acquisition](docs/07-user-acquisition.md)
- [08 — Thumbnails, launch & live-ops](docs/08-thumbnails-and-launch.md)

## License

MIT.
