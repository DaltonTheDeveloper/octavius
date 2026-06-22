# How RobloxForge improves itself over time

A one-shot generator plateaus. RobloxForge is built to get **better with every
game it ships and every piece of feedback it gets**, through a persistent
lessons-memory loop.

## The loop

```
        generate ──▶ review (AI) ──▶ lessons ──▶ memory
           ▲                                        │
           └──────── injected into next run ◀───────┘
                         ▲
        real-world feedback (CCU, retention, notes) feeds in here too
```

1. **Generate.** A run produces a game + artifacts (market report, GDD, QA,
   launch plan).
2. **Review.** A `ReviewerAgent` — a skeptical senior producer — scores the
   game's hit-potential and extracts **transferable lessons** scoped to each
   role (`market`, `design`, `engineering`, `ui`, `qa`, `marketing`, `global`).
   This runs automatically at the end of every `forge new` (disable with
   `--no-review`).
3. **Remember.** Lessons are appended to `memory/lessons.jsonl` (de-duplicated).
4. **Apply.** Before each agent runs, the lessons for its role are injected into
   its system prompt — so the next game is shaped by everything learned so far.

## Feeding in real outcomes

Reviews are the model's own judgement; **real metrics are ground truth**. When a
game is live, fold its actual performance back in:

```sh
forge feedback games/my-game --ccu 1200 --d1 14 --d7 4 \
  --note "players bounce on the tutorial; shop feels pay-to-win"
```

The reviewer turns those numbers/notes into concrete lessons (e.g.
*"design: D1 of 14% is below the 30% bar — cut the tutorial, get players into the
core loop in <10s"*) and stores them. Future games avoid the mistake.

## Inspecting and curating memory

```sh
forge lessons                 # everything learned
forge lessons --scope design  # just design lessons
forge review games/my-game    # re-critique an existing project, learn more
```

Because `memory/lessons.jsonl` is plain JSONL, you can **edit or prune it by
hand** and **commit it to git** — the project's accumulated wisdom travels with
the repo and is reviewable like any other change.

## Improving the system itself (beyond memory)

The lessons loop tunes *what the agents produce*. To improve *how the pipeline
works* (prompts, new agents, new knowledge docs), the normal software loop
applies: open a PR, get it reviewed (the repo ships with CI-friendly tests and
`ruff`), and extend `docs/` as Roblox changes. Good sources of system-level
improvements:

- Patterns that show up repeatedly in `forge lessons` → promote them from memory
  into an agent's base prompt or a `docs/` page.
- New Roblox features/algorithm changes → update the relevant `docs/` file (the
  agents read it automatically).
- Recurring QA findings → strengthen the engineering agent's prompt or add a
  template.
