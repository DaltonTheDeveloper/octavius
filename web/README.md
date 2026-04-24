# Octavius — marketing site

Next.js 14 (App Router) + Tailwind + Framer Motion. Designed to deploy to Vercel zero-config.

## Local dev

```sh
cd web
npm install
npm run dev
```

Visit http://localhost:3000.

## Deploy to Vercel

```sh
npx vercel        # link the project
npx vercel --prod # ship
```

Or push to GitHub and click "Import Project" on vercel.com — Vercel detects Next.js and configures the rest.

## Theme

- **Plasma** purple — Doc Ock signature.
- **Rust** orange — danger / approval color.
- **Chrome** cyan — Chrome capability accent.
- Dark-first. Glass cards. Animated SVG arms in the hero.

## Where to swap before launch

- `components/Nav.tsx`, `components/Footer.tsx`, `components/Hero.tsx` — replace `https://github.com/` with the real repo URL once published.
- `app/layout.tsx` — meta description / OG tags.
- `components/Marketplace.tsx` — labelled "(mockup)"; swap for real listings when the registry exists.
