"use client";
import { motion } from "framer-motion";
import { Eye, Box, ArrowDown } from "lucide-react";

const cards = [
  {
    title: "Pixel puppets",
    sub: "computer-use, Operator",
    body: "Universal but blind. Every action is a screenshot round-trip. UI changes break flows. Slow, fragile, no semantic memory.",
    icon: Eye,
    color: "text-rust-400",
  },
  {
    title: "Per-app sandboxes",
    sub: "VMs, browsers in a box",
    body: "Safe but walled. Claude can't see your real machine, your real files, or move things between apps. Demo-grade, not life-grade.",
    icon: Box,
    color: "text-chrome-400",
  },
];

export default function Problem() {
  return (
    <section className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
            THE TWO RUTS
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Everyone building agents picks the wrong floor.
          </h2>
          <p className="mt-3 text-ink-100/60 max-w-2xl mx-auto">
            You either let the model see nothing useful, or you give it a
            playground that doesn't matter. Octavius is the third path.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {cards.map((c, i) => {
            const Icon = c.icon;
            return (
              <motion.div
                key={c.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.6 }}
                className="glass rounded-2xl p-6"
              >
                <Icon className={c.color} size={28} />
                <div className="mt-4 text-xl font-semibold">{c.title}</div>
                <div className="text-xs font-mono text-ink-100/40 tracking-widest mt-1">
                  {c.sub.toUpperCase()}
                </div>
                <p className="mt-3 text-ink-100/70 text-sm leading-relaxed">{c.body}</p>
              </motion.div>
            );
          })}
        </div>

        <div className="flex justify-center mb-6">
          <ArrowDown className="text-plasma-400 animate-bounce" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="rounded-2xl p-8 md:p-10 bg-gradient-to-br from-plasma-500/15 via-ink-800 to-rust-500/10 border border-plasma-400/30 shadow-[0_0_60px_-20px_rgba(168,85,247,0.6)]"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-plasma-300 mb-2">
            THE OCTAVIUS WAY
          </div>
          <h3 className="text-2xl md:text-3xl font-semibold">
            Treat the OS as a graph, not a screen.
          </h3>
          <p className="mt-3 text-ink-100/80 max-w-3xl">
            A background daemon maintains a live graph of your machine —
            processes, volumes, projects, app state. Claude queries the graph
            instead of guessing from pixels. Every mutation goes through a
            capability with a defined inverse, written to an append-only
            journal you can roll back with one click.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
