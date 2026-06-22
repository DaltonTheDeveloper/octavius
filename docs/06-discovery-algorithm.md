# The discovery algorithm (how games get surfaced)

This is the single most important doc. The Roblox **"Recommended For You" (RFY)**
algorithm on the Home page decides who reaches millions. Design and marketing
should both optimize for it. Roblox publicly shares the signal list and their
relative importance. [discovery](https://create.roblox.com/docs/discovery)

## Two-stage system

1. **Retrieval** — picks a candidate subset of experiences from millions based on
   engagement/retention/monetization.
2. **Ranking** — personalizes the order of those candidates per user.

## The signals (in Roblox's stated priority order)

**Most important:**
1. **Play-through rate** (qualified plays ÷ recommendation impressions)
2. **First-play bounce rate** (negative) — measured at **<60s** and **61–180s**
3. **Play days per user**
4. **Playtime per user** (capped at **60 min/user/day** for the signal)

**Important:**
5. **Intentional co-play days per user** (joining/inviting/private-server play
   with friends — *not* matchmaking)
6. Qualified play sessions per user
7. Spend days per user
8. Robux spent per user

[signals](https://github.com/Roblox/creator-docs/blob/main/content/en-us/discovery.md)

## The two rules that change everything

1. **Per-user retention, not raw CCU.** Signals are per-user averages, so a small
   game with engaged players is *not* disadvantaged. Frequent **short** returns
   beat one long session — Roblox split the old engagement proxy into
   play-through / session-quality / spend precisely so "exciting thumbnail, no
   substance" games stop winning. Retention is scored over three windows: **D1,
   D2–7, D8–28** (expanded from 7 to 28 days).
   [optimizing-discovery](https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox)

2. **Ad-acquired users don't count.** Roblox "doesn't count the engagement,
   monetization, or retention of users first acquired from ads, curation,
   friends, search, social media, or any other source" in ranking — only users
   who **organically joined from RFY**. Ads can *accelerate consideration* (get
   you seen) but cannot lift your ranking. **Organic retention buys the
   algorithm; paid traffic buys a spike.**

## Retention benchmarks

Roblox shows your D1/D7/D30 vs 50th–90th percentile bands of similar experiences
(comparison only — doesn't change distribution). You can break retention down by
acquisition source. Community tiers (directional): D1 <20% = broken onboarding,
30–40% = good, 50%+ = exceptional.
[retention](https://create.roblox.com/docs/production/analytics/retention)
Players with ≥1 friend in-game show ~3× higher D30 (community figure).

## What developers do to please it

- **Fix the first 60–180 seconds.** Cut popups; get the player *playing* fast (an
  obby player should be jumping within ~10s). Every second of non-gameplay early
  costs new players. This is the highest-leverage thing you can do.
- **Drive repeat visits** (dailies, streaks, events inside the D1/D2-7/D8-28
  windows) and **playtime up to the 60-min cap**.
- **Encourage intentional co-play** — invite flows, play-with-friends rewards,
  the official Friend Referral System. Co-play sessions run ~1.9× longer and
  co-play is itself a ranking signal.
- **Ship updates often** so you surface in "Recently Updated" and keep return
  rates high (see `08`).
- **Don't violate metadata rules**: no giveaway-baiting ("FREE ROBUX!"), no
  mismatched title/thumbnail vs gameplay, no copycat metadata — all reduce
  distribution. Experiences are continuously reclassified, so fixes restore
  visibility.

## Tools to read the market

Official **Charts/Discover** (Popular, Top Trending, Top Earning), plus
[RoMonitor](https://romonitorstats.com/), [Rolimon's](https://www.rolimons.com/games),
[Rotrends](https://rotrends.com/), [RTrack](https://rtrack.live/). Your own
**Creator Hub Analytics** shows your performance against the ranking signals.

> Exact signal weights and the "qualified play" second-threshold are not
> published; treat specific QPTR percentages (developer-reported ~0.25–2%) as
> directional.
