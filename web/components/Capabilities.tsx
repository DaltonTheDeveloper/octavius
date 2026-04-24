"use client";
import { motion } from "framer-motion";

const groups = [
  {
    name: "Filesystem",
    color: "plasma",
    items: [
      { tool: "fs.move",   note: "move with inverse → undoable" },
      { tool: "fs.copy",   note: "copy file or directory" },
      { tool: "fs.write",  note: "atomic write, captures previous content" },
      { tool: "fs.delete", note: "trash-backed, restorable" },
    ],
  },
  {
    name: "Shell",
    color: "rust",
    items: [
      { tool: "shell.run", note: "exec with timeout, journaled (forward only)" },
    ],
  },
  {
    name: "Unreal Engine 5",
    color: "plasma",
    items: [
      { tool: "ue5.move_project",   note: "drops DDC/Intermediate/Saved across volumes" },
      { tool: "ue5.read_uproject",  note: "parsed engine association + plugins" },
      { tool: "ue5.launch_editor",  note: "open .uproject in UnrealEditor" },
    ],
  },
  {
    name: "Google Chrome",
    color: "chrome",
    items: [
      { tool: "chrome.open_url",  note: "new tab or replace active" },
      { tool: "chrome.list_tabs", note: "all windows, all tabs" },
      { tool: "chrome.run_js",    note: "JS in active tab (DevTools-grade)" },
    ],
  },
];

const colorMap: Record<string, string> = {
  plasma: "border-plasma-500/30 text-plasma-300",
  rust:   "border-rust-500/30 text-rust-400",
  chrome: "border-chrome-500/30 text-chrome-400",
};

export default function Capabilities() {
  return (
    <section id="capabilities" className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
            CAPABILITIES
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Eleven verbs, room for thousands.
          </h2>
          <p className="mt-3 text-ink-100/60 max-w-2xl mx-auto">
            Every capability is an async function. Drop a file in <code className="text-plasma-300">capabilities/</code>, register
            it, and Claude sees it. The marketplace will distribute these as
            signed bundles.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          {groups.map((g, gi) => (
            <motion.div
              key={g.name}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: gi * 0.08, duration: 0.5 }}
              className="glass rounded-2xl p-6"
            >
              <div className={`text-xs font-mono tracking-widest mb-4 ${colorMap[g.color].split(" ")[1]}`}>
                {g.name.toUpperCase()}
              </div>
              <div className="space-y-2">
                {g.items.map((it) => (
                  <div
                    key={it.tool}
                    className={`flex items-start justify-between gap-4 p-3 rounded-lg border bg-ink-900/40 ${colorMap[g.color]}`}
                  >
                    <code className="font-mono text-sm">{it.tool}</code>
                    <span className="text-xs text-ink-100/60 text-right">{it.note}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
