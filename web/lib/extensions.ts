import { db } from "./db";
import type { Extension, User } from "@prisma/client";

export type PublicExtension = Extension & { creator: Pick<User, "handle" | "name" | "image"> };

export async function listExtensions(): Promise<PublicExtension[]> {
  try {
    return await db.extension.findMany({
      where: { published: true },
      include: { creator: { select: { handle: true, name: true, image: true } } },
      orderBy: { downloads: "desc" },
    });
  } catch {
    return [];
  }
}

export async function getExtension(slug: string): Promise<PublicExtension | null> {
  try {
    return await db.extension.findUnique({
      where: { slug },
      include: { creator: { select: { handle: true, name: true, image: true } } },
    });
  } catch {
    return null;
  }
}

export async function getLicensed(userId: string, extensionId: string) {
  return db.license.findUnique({
    where: { userId_extensionId: { userId, extensionId } },
  });
}

export function parseTags(raw: string): string[] {
  try {
    const v = JSON.parse(raw);
    return Array.isArray(v) ? v : [];
  } catch {
    return [];
  }
}

export function accentClasses(accent: string) {
  const map: Record<string, string> = {
    plasma: "border-plasma-500/30 text-plasma-300",
    rust: "border-rust-500/30 text-rust-400",
    chrome: "border-chrome-500/30 text-chrome-400",
  };
  return map[accent] ?? map.plasma;
}
