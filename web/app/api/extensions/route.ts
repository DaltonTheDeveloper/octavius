import { NextResponse } from "next/server";
import { listExtensions } from "@/lib/extensions";

export async function GET() {
  const exts = await listExtensions();
  // Strip email-only fields for public API
  return NextResponse.json(
    exts.map((e) => ({
      id: e.id,
      slug: e.slug,
      name: e.name,
      tagline: e.tagline,
      tier: e.tier,
      accent: e.accent,
      iconEmoji: e.iconEmoji,
      tags: JSON.parse(e.tags || "[]"),
      downloads: e.downloads,
      creator: e.creator.handle,
      hasMembershipCode: !!e.membershipCode,
    })),
  );
}
