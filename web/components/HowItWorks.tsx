"use client";
import { motion } from "framer-motion";
import { GitBranch, Database, ShieldCheck, RotateCcw } from "lucide-react";

const steps = [
  {
    n: "01",
    title: "Live machine graph",
    body: "A daemon continuously snapshots running processes, mounted volumes, UE5 projects, Chrome state. Claude reads structured JSON, not screenshots.",
    Icon: Database,
  },
  {
    n: "02",
    title: "Capabilities, not clicks",
    body: "Verbs like fs.move, ue5.move_project, chrome.open_url. Each capability is an async function with parameters — Claude calls them via MCP.",
    Icon: GitBranch,
  },
  {
    n: "03",
    title: "Approval bus",
    body: "Risky calls land in the sidebar UI as pending actions. You see the summary, dry-run preview, and parameters. Tap Approve or Reject.",
    Icon: ShieldCheck,
  },
  {
    n: "04",
    title: "Reversible journal",
    body: "Every committed action records its inverse to ~/.octavius/journal.jsonl. One key undoes the last N. Filesystem, project moves, deletes — all rewindable.",
    Icon: RotateCcw,
  },
];

export default function HowItWorks() {
  return (
    <section id="how" className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
            HOW IT WORKS
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Four parts, one process.
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          {steps.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
              className="group relative glass rounded-2xl p-6 hover:border-plasma-400/50 transition"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 h-12 w-12 rounded-xl bg-plasma-500/15 grid place-items-center border border-plasma-500/30 group-hover:bg-plasma-500/25 transition">
                  <s.Icon className="text-plasma-300" size={20} />
                </div>
                <div>
                  <div className="text-xs font-mono text-plasma-400 tracking-widest">{s.n}</div>
                  <div className="mt-1 text-lg font-semibold">{s.title}</div>
                  <p className="mt-2 text-sm text-ink-100/70 leading-relaxed">{s.body}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="mt-12 p-6 rounded-2xl bg-ink-900/60 border border-plasma-500/20 font-mono text-sm overflow-x-auto"
        >
          <div className="text-ink-100/40 mb-3 text-xs tracking-widest">
            ~/.claude — ONE LINE TO INSTALL
          </div>
          <code className="text-plasma-300">
            claude mcp add --transport http octavius http://127.0.0.1:7777/mcp
          </code>
        </motion.div>
      </div>
    </section>
  );
}
