"use client";
import { motion } from "framer-motion";
import { Apple, Terminal, ArrowRight, ShieldAlert } from "lucide-react";

export default function Download() {
  return (
    <section id="download" className="relative py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
            DOWNLOAD
          </div>
          <h2 className="text-3xl md:text-5xl font-semibold tracking-tight">
            Try it on your machine.
          </h2>
          <p className="mt-3 text-ink-100/60 max-w-2xl mx-auto">
            macOS 13+. Apple Silicon or Intel. Two paths — pick one.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="rounded-2xl p-6 border border-plasma-500/30 bg-gradient-to-br from-plasma-500/10 via-ink-900 to-ink-800 hover:scale-[1.01] transition"
          >
            <Apple size={28} className="text-plasma-300 mb-4" />
            <div className="font-semibold text-lg">Octavius.app</div>
            <div className="text-xs font-mono tracking-widest text-plasma-400 mt-1">
              MENUBAR APP · DMG
            </div>
            <p className="mt-3 text-sm text-ink-100/70 leading-relaxed">
              Drag-to-Applications DMG. Lives in your menubar 🐙. Manages the
              daemon, shows pending approvals, recent runs, and your installed
              extensions.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 text-xs text-rust-400 font-mono">
              <ShieldAlert size={12} /> Unsigned (right-click → Open the first time)
            </div>
            <a
              href="https://github.com/DaltonTheDeveloper/octavius/releases"
              className="mt-5 group inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-br from-plasma-500 to-plasma-600 text-white font-semibold hover:brightness-110 transition w-full justify-center"
            >
              Download .dmg <ArrowRight size={14} className="group-hover:translate-x-1 transition" />
            </a>
            <div className="mt-3 text-[11px] text-ink-100/40 text-center">
              v0.1 · ~30 MB · Apple Silicon + Intel
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.08, duration: 0.5 }}
            className="rounded-2xl p-6 border border-rust-500/30 bg-gradient-to-br from-rust-500/10 via-ink-900 to-ink-800 hover:scale-[1.01] transition"
          >
            <Terminal size={28} className="text-rust-400 mb-4" />
            <div className="font-semibold text-lg">From source</div>
            <div className="text-xs font-mono tracking-widest text-rust-400 mt-1">
              OPEN-SOURCE · GITHUB
            </div>
            <p className="mt-3 text-sm text-ink-100/70 leading-relaxed">
              For developers who want to fork, hack, or write extensions. Clone
              the repo, run the daemon, hook it into Claude Code with one MCP
              command.
            </p>
            <pre className="mt-5 p-3 bg-ink-950/70 border border-rust-500/20 rounded-lg text-[11px] font-mono text-rust-300 overflow-x-auto leading-relaxed">
              git clone https://github.com/DaltonTheDeveloper/octavius{"\n"}
              cd octavius && ./scripts/install.sh{"\n"}
              octavius-bus{"\n"}
              {"\n"}
              # then in Claude Code:{"\n"}
              claude mcp add --transport http \\{"\n"}
              {"  "}octavius http://127.0.0.1:7777/mcp
            </pre>
            <a
              href="https://github.com/DaltonTheDeveloper/octavius"
              className="mt-5 group inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-rust-500/40 bg-rust-500/10 text-rust-300 font-semibold hover:bg-rust-500/20 transition w-full justify-center"
            >
              View on GitHub <ArrowRight size={14} className="group-hover:translate-x-1 transition" />
            </a>
            <div className="mt-3 text-[11px] text-ink-100/40 text-center">
              MIT · 48 capabilities · &lt; 5k LOC
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-10 grid md:grid-cols-3 gap-4 text-sm"
        >
          {[
            { k: "48 capabilities", v: "fs, ue5, chrome, epic, vision, binary, jobs, volume, ui — and growing." },
            { k: "Resumable jobs", v: "Long flows checkpoint to disk. Daemon restart? `jobs.resume <id>` and pick up." },
            { k: "Reverse-engineering", v: "binary.analyze cracks open any .app. Read its ObjC classes, embedded URLs, entitlements." },
          ].map((x) => (
            <div key={x.k} className="rounded-xl p-4 bg-ink-900/50 border border-plasma-500/20">
              <div className="text-plasma-300 font-semibold text-sm">{x.k}</div>
              <div className="text-xs text-ink-100/70 mt-1">{x.v}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
