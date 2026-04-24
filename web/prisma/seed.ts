import { PrismaClient } from "@prisma/client";

const db = new PrismaClient();

async function main() {
  // Seed a demo creator + three extensions so the marketplace renders
  // immediately after `npx prisma db push && npx tsx prisma/seed.ts`.
  const creator = await db.user.upsert({
    where: { handle: "dalton" },
    update: {},
    create: {
      email: "dalton@example.com",
      handle: "dalton",
      name: "Dalton",
      isCreator: true,
      bio: "Building Octavius.",
    },
  });

  const samples = [
    {
      slug: "ue5-blueprint-tools",
      name: "UE5 Blueprint Tools",
      tagline: "Read Blueprint graphs, spawn actors, hot-reload C++.",
      description:
        "Deep integration with UnrealEditor's Python API. Query, mutate, and reload without leaving Claude Code.",
      tier: "free",
      accent: "plasma",
      iconEmoji: "🎮",
      tags: '["unreal","blueprints","gamedev"]',
      downloads: 1280,
      membershipNote:
        "Public & free for now. Eventually paid — my YouTube members will get a rotating code for free access.",
    },
    {
      slug: "blender-bridge",
      name: "Blender Bridge",
      tagline: "Open files, render, export FBX/GLTF, scene queries.",
      description:
        "Full Blender Python API exposed as capabilities. Render frame, adjust materials, batch-export the active scene.",
      tier: "free",
      accent: "rust",
      iconEmoji: "🧊",
      tags: '["blender","vfx","3d"]',
      downloads: 842,
    },
    {
      slug: "obsidian-graph",
      name: "Obsidian Graph",
      tagline: "Search, read, write notes. Manage tags. Inverse-safe.",
      description:
        "Every edit journaled with an undo. Great for 'summarize my last week of notes' or 'refactor these tags.'",
      tier: "free",
      accent: "chrome",
      iconEmoji: "📘",
      tags: '["notes","obsidian","pkm"]',
      downloads: 421,
    },
  ];

  for (const s of samples) {
    await db.extension.upsert({
      where: { slug: s.slug },
      update: {},
      create: { ...s, creatorId: creator.id },
    });
  }

  console.log("seeded:", await db.extension.count(), "extensions");
}

main().finally(() => db.$disconnect());
