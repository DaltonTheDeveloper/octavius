"use client";
import { motion } from "framer-motion";
import { Package, Star, Download, Sparkles } from "lucide-react";

const sample = [
  {
    name: "blender-bridge",
    author: "@vfxguild",
    desc: "Blender capabilities — open file, render, export, scene query.",
    pulls: "12.4k",
    stars: 412,
    color: "rust",
  },
  {
    name: "obsidian-graph",
    author: "@knowledgeworks",
    desc: "Read/write notes, search vault, manage tags. Inverse-safe.",
    pulls: "8.1k",
    stars: 287,
    color: "plasma",
  },
  {
    name: "spotify-driver",
    author: "@dalton",
    desc: "Playback, queue, playlist edits via Spotify Connect API.",
    pulls: "3.6k",
    stars: 94,
    color: "chrome",
  },
  {
    name: "ue5-blueprint-tools",
    author: "@gameframework",
    desc: "Read Blueprint graphs, spawn actors, hot-reload C++.",
    pulls: "21.8k",
    stars: 1102,
    color: "plasma",
  },
];

const colorMap: Record<string, string> = {
  plasma: "border-plasma-500/30 bg-plasma-500/5",
  rust: "border-rust-500/30 bg-rust-500/5",
  chrome: "border-chrome-500/30 bg-chrome-500/5",
};

export default function Marketplace() {
  return (
    <section id="marketplace" className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-rust-500/30 bg-rust-500/10 text-xs font-mono tracking-widest text-rust-400 mb-4">
            <Sparkles size={12} /> COMING SOON
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight">
            A marketplace for arms.
          </h2>
          <p className="mt-3 text-ink-100/60 max-w-2xl mx-auto">
            Anyone can publish a capability bundle. Signed releases, version
            pinning, sandboxed manifests. The community grows the surface area
            without anyone writing pixel-puppet code.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-4">
          {sample.map((s, i) => (
            <motion.div
              key={s.name}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06, duration: 0.5 }}
              className={`rounded-2xl p-5 border ${colorMap[s.color]} hover:scale-[1.01] transition`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-ink-900 grid place-items-center border border-ink-700">
                    <Package size={18} className="text-ink-100/70" />
                  </div>
                  <div>
                    <div className="font-mono font-semibold">{s.name}</div>
                    <div className="text-xs text-ink-100/50">{s.author}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-ink-100/60">
                  <span className="inline-flex items-center gap-1"><Star size={12} /> {s.stars}</span>
                  <span className="inline-flex items-center gap-1"><Download size={12} /> {s.pulls}</span>
                </div>
              </div>
              <div className="mt-3 text-sm text-ink-100/70">{s.desc}</div>
              <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono bg-ink-950/70 border border-ink-700 text-ink-100/50">
                octavius install {s.name}
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-10 text-center text-xs text-ink-100/40 font-mono tracking-widest">
          (mockup — real registry shipping after v0.2)
        </div>
      </div>
    </section>
  );
}
