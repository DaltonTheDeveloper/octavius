import { handlers, authConfigured } from "@/auth";

// When auth isn't configured (no env vars), return a helpful 503 instead of crashing.
const stub = async () =>
  new Response(
    JSON.stringify({
      error: "auth_not_configured",
      hint: "Set AUTH_SECRET, AUTH_GITHUB_ID, AUTH_GITHUB_SECRET in .env / Vercel project env vars.",
    }),
    { status: 503, headers: { "content-type": "application/json" } },
  );

export const GET = authConfigured ? handlers.GET : stub;
export const POST = authConfigured ? handlers.POST : stub;
