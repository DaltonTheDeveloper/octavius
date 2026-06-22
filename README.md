# 🎮 RobloxForge

**An AI pipeline that automates Roblox game development end-to-end** — market
research, game design, Luau engineering, UI/UX, QA, and a free-growth launch plan
— and hands you a ready-to-open [Rojo](https://rojo.space) project.

You give it an idea (or nothing). It researches what's trending, picks a concept
that can grow organically and monetize cleanly, writes a game design document,
generates server-authoritative Luau and a mobile-first UI, reviews the code for
exploits and data loss, writes tests, and produces a launch playbook for getting
your first players **for free**.

It **runs on [Claude Code](https://docs.claude.com/en/docs/claude-code)** — the
local `claude` CLI on your Claude subscription, so there's **no API key and no
per-token billing** by default. And it **improves itself over time**: every run
is self-reviewed, and you can feed back real-world results — the lessons are
remembered and applied to future games (see
[docs/09](docs/09-self-improvement.md)).

It is grounded in a researched [knowledge base](docs/) of how Roblox games are
actually built, shipped, and grown.

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
                                                                              │
                                                               Self-review ──▶ lessons ──▶ memory/
                                                                              ▲                │
                                          real-world feedback (forge feedback) ┘   injected into next run
```

Each stage is a specialist [agent](robloxforge/agents) with a role-specific
prompt, fed the relevant [`docs/`](docs/) as grounding context. Every stage's
output is a typed artifact consumed by the next. The result is written to disk as
a Rojo project (`src/shared`, `src/server`, `src/client`) plus a `forge/` folder
holding the market report, GDD, QA report, and launch plan.

## Install

```sh
pip install -e .            # or: pip install -e ".[dev]"
```

That's it — no API key. RobloxForge shells out to the `claude` CLI, so just make
sure Claude Code is installed and you've signed in once:

```sh
claude          # sign in to your Claude subscription (one time)
forge info      # should show: claude CLI (default backend) -> found
```

Prefer the Anthropic API instead (e.g. for unattended CI)? Install the extra and
set a key, then pass `--backend api`:

```sh
pip install -e ".[api]" && export ANTHROPIC_API_KEY=sk-...
```

## Use

```sh
# Generate a complete game from an idea (or a vague direction).
# Self-reviews at the end and remembers what it learned.
forge new "a chill pet-collecting game with a steal-and-defend twist"

# Just see ranked, buildable concepts for an idea
forge research "horror co-op for mobile"

# Improve over time -------------------------------------------------
forge review games/<your-game>                 # re-critique; learn lessons
forge feedback games/<your-game> --d1 14 --ccu 1200 \
  --note "players bounce on the tutorial"      # learn from REAL outcomes
forge lessons                                   # see everything it has learned

# Utilities
forge info                                       # backend, CLI, lessons, toolchain
forge publish MyGame.rbxlx                        # publish via Open Cloud (optional)
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
├── cli.py            # `forge` CLI (new / research / review / feedback / lessons / info / publish)
├── pipeline.py       # orchestrates the 6-stage pipeline + self-review
├── backends.py       # Claude Code (CLI, default) and Anthropic API backends
├── llm.py            # backend-agnostic facade (text + structured parsing)
├── memory.py         # persistent "lessons" store — the self-improvement loop
├── reviewing.py      # review/feedback an existing project, fold lessons into memory
├── models.py         # typed artifacts (GDD, MarketReport, LaunchPlan, ReviewResult, ...)
├── knowledge.py      # injects docs/ into each agent
├── codegen.py        # file-delimiter protocol for multi-file code generation
├── agents/           # market, design, engineering, UI/UX, QA, marketing, reviewer
└── roblox/
    ├── rojo.py       # scaffolds a ready-to-open Rojo project
    ├── opencloud.py  # Open Cloud client (publish, datastore, messaging, assets)
    └── templates.py  # default.project.json, rokit/wally/selene/.luaurc
docs/                 # the researched Roblox knowledge base (also great reading)
memory/lessons.jsonl  # what the system has learned (grows over time; commit it)
```

## Configuration

| Env var | Purpose |
|---|---|
| `FORGE_BACKEND` | `claude-code` (default, no key) or `api`. |
| `FORGE_MODEL` | Model id or CLI alias (default `claude-opus-4-8`). |
| `FORGE_EFFORT` | `low`/`medium`/`high`/`xhigh`/`max` (default `high`). |
| `FORGE_OUTPUT` | Output directory (default `games/`). |
| `FORGE_MEMORY` | Lessons file (default `memory/lessons.jsonl`). |
| `ANTHROPIC_API_KEY` | Only for `--backend api`. |
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
- [09 — How the system improves itself](docs/09-self-improvement.md)

## License

MIT.
