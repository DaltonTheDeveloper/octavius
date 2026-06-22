# Thumbnails, launch, live-ops & compliance

## Thumbnails & icons (CTR is everything)

Your icon/thumbnail decide click-through, which feeds play-through rate (`06`).

**Specs:** thumbnails are **16:9, ideally 1920×1080**; formats .jpg/.gif/.png/
.tga/.bmp, **<3 MB** each; up to **10** images/videos per page; **3 video
uploads/month**; consoles/VR don't show video thumbnails.
[thumbnails](https://create.roblox.com/docs/production/publishing/thumbnails)

**A/B test natively:** personalization (serving the best thumbnail per user)
**only starts with ≥2 active thumbnails**; keep **2–5** active. The dashboard
reports impressions, plays, and QPTR per thumbnail. **Change one variable at a
time** (background, face, or text) to learn what moves CTR.

**Design conventions (community, directional):** one **focal moment** (a shocked/
exaggerated avatar face, a big arrow, danger/high-contrast color), **high-
contrast legible text** (white with dark outline), **short punchy words**
("SECRET", "IMPOSSIBLE"). **Don't put key elements at the bottom** — the player-
count overlay covers them.

**Must be authentic:** thumbnails/videos can't misrepresent gameplay (no fake
footage, real-life clips, or misleading claims) or they're removed. Clickbait
also fails on QPTR — players bounce, and the algorithm punishes bounces.

## Launch & live-ops

**Soft launch small, iterate on retention before scaling.** Ship a small playable
scope, watch CCU/session length/retention curves, fix the funnel, *then* expand.
The 2024–25 breakouts were small teams shipping fast iteration cycles.

**Update cadence (official): weekly to monthly.** Roblox: "Without LiveOps
updates, even dedicated players lose interest." Lightweight cadence releases (new
cosmetics/maps reusing existing systems) keep "Recently Updated" fresh; reserve
big new systems for major updates every few months. Grow a Garden runs a strict
**weekly Saturday** update and became the top game by daily CCU.
[liveops](https://create.roblox.com/docs/production/game-design/liveops-essentials)

**Seasonal/events:** plan around KPIs, **announce in advance** ("communicating the
event in advance encourages players to schedule their return"), and measure the
**retention lift** in event vs non-event weeks.
[liveops-planning](https://create.roblox.com/docs/production/game-design/liveops-planning)

**A practical launch checklist:**
1. Build the in-game viral loop first (referral + play-with-friends rewards).
2. Nail the first 60–180s funnel (no popup walls; player playing in ~10s).
3. Make 3–5 thumbnails + a strong icon; A/B from day one.
4. SEO the title/description (`07`).
5. Stand up one community (Discord or Group) and engage in it personally.
6. Start a daily TikTok/Shorts clipping habit; chase reaction-worthy moments.
7. Launch/update on a **Saturday**; ship a visible update every 1–4 weeks.
8. Watch analytics; iterate retention before chasing scale.

## Compliance & safety (don't get taken down)

- **Community Standards** span Safety, Civility, Integrity, Security. Prohibited:
  real-world tragedies, gore beyond your rating, sexual content, illegal goods,
  profanity, IP infringement, scams, unauthorized ads.
  [standards](https://about.roblox.com/community-standards)
- **Content maturity questionnaire is mandatory** — skip it and Roblox restricts
  playability for everyone. Labels: Minimal / Mild / Moderate / Restricted, with
  age gating; **Restricted = age-verified 18+ only**. N/A-rated games were made
  unplayable by end of Sept 2025.
  [content-maturity](https://github.com/Roblox/creator-docs/blob/main/content/en-us/production/promotion/content-maturity.md)
- **Gambling is banned**; "mystery boxes"/loot mechanics ("Paid Random Items")
  are allowed only with **disclosed odds summing to 100%**, every outcome must
  give a benefit, and you must gate them in restricted countries (AU, BE, NL, UK,
  BR) via `PolicyService:ArePaidRandomItemsRestricted`.
  [paid random items](https://devforum.roblox.com/t/clarifying-requirements-for-paid-random-items/4654622)
- **Age checks for chat** (Facial Age Estimation) rolled out globally early 2026;
  chat is restricted to similar age bands; **social-media links inside
  experiences are restricted** from early 2026; Studio Team Create needs age
  verification.
  [age checks](https://about.roblox.com/newsroom/2025/11/roblox-requires-age-checks-limits-minor-and-adult-chat)

> Marketing CTR percentages from design blogs are unverified; specs, A/B
> mechanics, cadence guidance, and compliance rules are from official Roblox
> sources.
