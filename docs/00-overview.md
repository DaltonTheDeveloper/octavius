# Roblox game development — the whole picture

This knowledge base is the distilled research behind RobloxForge. It covers the
entire pipeline of making a *hit* Roblox game and getting your first players for
free. The agents read these files as grounding context, and you can read them as
a field manual.

## The shape of the opportunity (2025–2026)

- Roblox set an all-time platform record of **47.4M concurrent users** (Aug 2025),
  surpassing Steam's all-time ~41.2M peak.
  [src](https://www.pocketgamer.biz/robloxs-peak-concurrent-user-count-hits-record-474m-as-steal-a-brainrot-and-grow-a-garden-compete/)
- ~**132M daily active users**; Roblox paid creators **$1B+ in a single quarter**
  (Q3 2025).
  [src](https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox)
- Total creator payouts reached **$1.50B in 2025** (up from $0.92B in 2024).
  [SEC FY2025](https://www.sec.gov/Archives/edgar/data/1315098/000110465926044380/rblx-20251231xars.pdf)
- Multiple 2025 breakout hits were built by **tiny teams in days** (Grow a Garden
  reportedly built by a teenager "in like three days"). The barrier is taste and
  speed, not budget.

The flip side: earnings are **extremely concentrated**. The median DevEx
participant earned **~$1,575/year**; the top 10 averaged **$33.9M**.
[Economic Impact Report](https://about.roblox.com/newsroom/2025/09/roblox-annual-economic-impact-report)
Most experiences earn little. Winning requires nailing retention and discovery,
not just shipping.

## The pipeline RobloxForge automates

1. **Market research** — find a concept that can grow organically and monetize
   cleanly (`05`, `06`).
2. **Game design** — a tight GDD built around retention and a short core loop
   (`04`, `05`).
3. **Engineering** — server-authoritative Luau, persistence, economy (`01`, `04`).
4. **UI/UX** — mobile-first, engagement-focused interface (`01`).
5. **QA** — exploit/data-loss review + automated tests (`01`, `04`, `02`).
6. **Marketing / user acquisition** — free growth: short-form video, referral
   loops, community, relentless updates (`07`, `08`).
7. **Publish & live-ops** — Open Cloud automation and update cadence (`03`, `08`).

## The one idea that ties it together

The Roblox discovery algorithm rewards **per-user retention and co-play**, not
raw concurrent users, and it **ignores users acquired from ads**. So the entire
game — design, code, UI, *and* marketing — should optimize for: a fast,
non-bouncing first session, frequent short return visits, playing with friends,
and a constant stream of updates. Build for the algorithm, grow for free. See
`06` for the exact signals.

> Every factual claim in these docs is sourced. Where a figure comes from a
> third-party/community source rather than official Roblox docs, it is flagged.
> Numbers move fast on Roblox — verify anything load-bearing against the linked
> source before betting on it.
