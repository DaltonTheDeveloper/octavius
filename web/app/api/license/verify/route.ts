import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";

// Called by the Octavius daemon on install + periodically.
export async function POST(req: NextRequest) {
  const { installKey, slug } = (await req.json().catch(() => ({}))) as {
    installKey?: string;
    slug?: string;
  };
  if (!installKey || !slug) {
    return NextResponse.json({ valid: false, error: "installKey + slug required" }, { status: 400 });
  }

  const ext = await db.extension.findUnique({ where: { slug } });
  if (!ext) return NextResponse.json({ valid: false, error: "extension not found" }, { status: 404 });

  const license = await db.license.findFirst({
    where: { installKey, extensionId: ext.id, revokedAt: null },
    include: { user: { select: { email: true, handle: true } } },
  });
  if (!license) {
    return NextResponse.json({ valid: false, error: "no active license" }, { status: 401 });
  }
  if (license.expiresAt && license.expiresAt < new Date()) {
    return NextResponse.json({ valid: false, error: "expired" }, { status: 401 });
  }

  return NextResponse.json({
    valid: true,
    license: {
      id: license.id,
      source: license.source,
      user: license.user,
      extension: { id: ext.id, slug: ext.slug, name: ext.name, tier: ext.tier },
    },
  });
}
