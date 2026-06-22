# Market trends & monetization

## What's hot (2025–2026)

The dominant format is **trend-driven "brainrot"/collection** games with a simple
loop (buy → generate income → steal/defend), plus **idle/incremental + collection**
and **survival/horror**.

- **Steal a Brainrot** — peaked **25.4M CCU** (Oct 7, 2025), the highest CCU ever
  for any single video game; tens of billions of visits.
  [src](https://www.pocketgamer.biz/robloxs-steal-a-brainrot-becomes-first-game-to-surpass-25m-concurrent-players/)
- **Grow a Garden** — peaked ~**21–22M CCU**; fastest Roblox game to 1B visits
  (33 days). Built fast by a tiny team.
  [src](https://en.wikipedia.org/wiki/Grow_a_Garden)
- **99 Nights in the Forest** — survival; 10B+ visits in months; first survival
  game to sustain 1M+ avg CCU.
- **Evergreen mainstays**: Brookhaven RP (~69B visits), Blox Fruits, Adopt Me,
  Murder Mystery 2, Dress to Impress (~56.7B), The Strongest Battlegrounds.
- **Anime** (Blue Lock: Rivals, Anime Vanguards) and **battlegrounds/fighting**
  are fast-growing.

Market is concentrating hard: the #1 game's share of top-10 visits grew from
**22% (Q1 2025) to 43% (Q4 2025)**, and hits fade fast — even Steal a Brainrot
lost ~30% of peak monthly visits by year-end.
[Newzoo](https://gamedevreports.substack.com/p/newzoo-top-roblox-games-in-2025)

## Saturation vs opportunity

- **Simulators** — saturated but consistently profitable (natural progression/pet
  monetization). One dev raised revenue $3k→$18k/mo by adding a 2× coin pass.
- **Brainrot/steal clones** — peak saturation; the originators are filing
  lawsuits against imitators. Riding a *fresh* meme beats cloning a stale one.
- **Tycoons** — moderately saturated, beginner-friendly, high search intent,
  lowest dev-cost-to-return.
- **Opportunity**: **hybrid genres** (Fisch = simulator + RPG + social, ~1.5B
  visits), **social/hangout**, **themed RPG/roleplay**, fashion/UGC.
  [genres](https://www.robloxdesk.com/most-profitable-roblox-game-genres-2026/)

**A winning idea has**: a sub-5-minute core loop, visible progression, a social
trigger that pulls in a 2nd player, and monetization that doesn't block fun.
"A tycoon shipped in 6 weeks beats a roleplay city abandoned in 6 months."

## What counts as a "hit"

- Solo/small viable income: hundreds–low-thousands CCU (some solo obby devs report
  ~$22k–28k/mo at scale — directional).
- Trending: tens of thousands CCU. Mega-hit tier (2025–26): **1M–25M CCU**.
- Roblox analytics benchmark scorecards activate at **100+ DAU**.

## Monetization

**Keep 70% of in-experience purchases** — the standard marketplace fee is 30%.
[fees](https://create.roblox.com/docs/marketplace/marketplace-fees-and-commissions)
(Avatar items and cross-experience sales split differently.)

- **Passes** (formerly Game Passes): one-time Robux purchase for a **permanent**
  privilege (2× coins, VIP, extra slot). Use for permanent unlocks.
- **Developer Products**: purchasable **repeatedly** (currency packs, consumables,
  revives). Use for anything consumable.
- **Subscriptions**: recurring monthly benefits inside an experience.
  [monetization](https://create.roblox.com/docs/production/monetization)

In Luau, use `MarketplaceService` to prompt purchases
(`PromptGamePassPurchase` / `PromptProductPurchase`), check ownership
(`UserOwnsGamePassAsync`), and grant via `ProcessReceipt` (dev products) — always
server-side.

### Creator Rewards (replaced Premium Payouts, July 24, 2025)

- **Daily Engagement Rewards**: **5 Robux** when an "Active Spender" spends ≥10
  minutes/day in your experience (first 3 experiences/day).
- **Audience Expansion Rewards**: **35% rev-share on the first $100** a new/
  returning user spends in their first two months on the platform.
- "Active Spender" = spent ≥**$9.99** in the last 60 days.
  [Creator Rewards](https://devforum.roblox.com/t/introducing-creator-rewards-earn-more-by-growing-the-community/3777628)

### DevEx (cash out)

Current rate: **$0.0038 / Earned Robux = $380 per 100,000** (8.5% increase as of
Sept 5, 2025; was $350/100k).
[DevEx increase](https://devforum.roblox.com/t/increasing-devex-%E2%80%94-creators-will-now-earn-85-more/3920159)
Minimum ~30,000 Earned Robux to cash out (verify), via Tipalti; only "Earned"
Robux qualify. A higher US-18+ rate (~$540/100k) has been reported (verify).

### Reality check

Earnings are top-heavy: median DevEx participant **~$1,575/yr**, top-1,000
average **~$820k**, top-10 average **$33.9M**. Most experiences earn little —
retention and discovery are what separate them.
[Economic Impact](https://about.roblox.com/newsroom/2025/09/roblox-annual-economic-impact-report)

## Monetization design rules

- **Never gate the fun.** Sell acceleration (2× coins, auto-collect), convenience,
  and cosmetics — not the ability to play.
- **First-session free value**; introduce purchases after the player is hooked.
- Price for a young, mostly non-paying audience; conversion is small, so make the
  free loop great and let whales accelerate.
