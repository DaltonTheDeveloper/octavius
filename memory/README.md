# memory/

This is where RobloxForge keeps what it has **learned** — `lessons.jsonl`, an
append-only, de-duplicated list of transferable lessons distilled from self-
reviews (`forge new`, `forge review`) and real-world feedback (`forge feedback`).

Before each agent runs, the lessons for its role are injected into its prompt, so
the system improves with every game it ships. The file is plain JSONL — diff it,
prune it by hand, and **commit it** so the project's accumulated wisdom travels
with the repo.

See [docs/09-self-improvement.md](../docs/09-self-improvement.md) for the full
loop. Inspect with `forge lessons`.
