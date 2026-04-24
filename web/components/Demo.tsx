"use client";
import { motion } from "framer-motion";
import { Check, X, AlertTriangle } from "lucide-react";

export default function Demo() {
  return (
    <section className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
            THE LOOP
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Claude proposes. You approve. Octavius executes.
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-5 gap-4 items-stretch">
          {/* Claude Code pane */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="md:col-span-2 glass rounded-2xl p-5 font-mono text-xs leading-relaxed"
          >
            <div className="text-ink-100/40 mb-3 tracking-widest">CLAUDE CODE</div>
            <div className="text-plasma-300">$ claude</div>
            <div className="mt-2 text-ink-100/80">
              &gt; move my UE5 project Frostbite to /Volumes/Backup
            </div>
            <div className="mt-3 text-ink-100/60">
              <span className="text-rust-400">●</span> querying graph...
            </div>
            <div className="text-ink-100/60">
              <span className="text-rust-400">●</span> found Frostbite (24.1 GB)
            </div>
            <div className="text-ink-100/60">
              <span className="text-rust-400">●</span> /Volumes/Backup has 412 GB free
            </div>
            <div className="text-ink-100/60">
              <span className="text-plasma-400">→</span> proposing ue5.move_project
            </div>
            <div className="mt-3 text-ink-100/40">
              waiting for your approval in the Octavius sidebar...
            </div>
          </motion.div>

          {/* Approval card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="md:col-span-3 rounded-2xl border border-rust-500/40 bg-gradient-to-br from-ink-900 to-ink-800 p-5 shadow-[0_0_60px_-20px_rgba(251,146,60,0.5)]"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-semibold text-lg">
                  Move UE5 project <span className="text-plasma-300">Frostbite</span> to /Volumes/Backup
                </div>
                <div className="font-mono text-xs text-ink-100/40 mt-1">ue5.move_project</div>
              </div>
              <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full bg-rust-500/20 text-rust-400">
                <AlertTriangle size={12} /> medium
              </span>
            </div>
            <div className="mt-4 text-xs font-mono bg-ink-950/70 rounded-lg p-3 border border-plasma-500/20 leading-relaxed">
              src_dir: /Users/dalton/UnrealProjects/Frostbite (24.1 GB)<br />
              dst_dir: /Volumes/Backup/Frostbite<br />
              drop_ddc: true (skipping DerivedDataCache, Saved, Intermediate)<br />
              estimated transfer: ~6 min over USB3
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <button className="flex items-center justify-center gap-2 rounded-xl py-2.5 bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 font-semibold hover:bg-emerald-500/25 transition">
                <Check size={16} /> Approve
              </button>
              <button className="flex items-center justify-center gap-2 rounded-xl py-2.5 bg-rust-500/15 border border-rust-500/40 text-rust-300 font-semibold hover:bg-rust-500/25 transition">
                <X size={16} /> Reject
              </button>
            </div>
            <div className="mt-3 text-[11px] text-ink-100/40 text-center">
              auto-rejects in 5:00 if you don't act
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
