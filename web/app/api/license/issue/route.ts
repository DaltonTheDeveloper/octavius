import { NextRequest, NextResponse } from "next/server";
import { auth, authConfigured } from "@/auth";
import { db } from "@/lib/db";
import { randomToken } from "@/lib/ids";

export async function POST(req: NextRequest) {
  if (!authConfigured) {
    return NextResponse.json({ error: "auth_not_configured" }, { status: 503 });
  }
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ error: "unauthenticated" }, { status: 401 });

  const { extensionId } = (await req.json().catch(() => ({}))) as { extensionId?: string };
  if (!extensionId) return NextResponse.json({ error: "extensionId required" }, { status: 400 });

  const user = await db.user.findUnique({ where: { email: session.user.email } });
  if (!user) return NextResponse.json({ error: "no user" }, { status: 401 });

  const ext = await db.extension.findUnique({ where: { id: extensionId } });
  if (!ext) return NextResponse.json({ error: "extension not found" }, { status: 404 });

  // Beta: all tiers are claimable free. When paid lands, gate here.
  const existing = await db.license.findUnique({
    where: { userId_extensionId: { userId: user.id, extensionId } },
  });
  if (existing) return NextResponse.json({ license: existing, alreadyOwned: true });

  const license = await db.license.create({
    data: {
      userId: user.id,
      extensionId,
      source: ext.tier === "free" ? "free" : "beta",
      installKey: randomToken(),
    },
  });
  await db.extension.update({ where: { id: extensionId }, data: { downloads: { increment: 1 } } });

  return NextResponse.json({ license });
}
