"use client";
import { motion } from "framer-motion";
import { ArrowRight, Cpu } from "lucide-react";
import Arms from "./Arms";

export default function Hero() {
  return (
    <section className="relative pt-28 pb-24 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-50 pointer-events-none" />
      <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-plasma-500/30 bg-plasma-500/10 text-xs font-mono tracking-widest text-plasma-300"
          >
            <Cpu size={12} /> v0.1 — LOCAL HOST BUS
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="mt-5 text-5xl md:text-7xl font-semibold tracking-tight leading-[1.05]"
          >
            <span className="text-glow text-plasma-300">Eight arms</span><br />
            <span className="text-white">for Claude.</span><br />
            <span className="text-ink-100/60 text-3xl md:text-4xl font-normal">
              None of the insanity.
            </span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, duration: 0.7 }}
            className="mt-6 text-lg text-ink-100/70 max-w-xl"
          >
            A local agent that gives Claude structured, reversible access to
            your whole machine — your engine, your browser, your files. Every
            risky action queues for one-click approval. Every committed action
            is undoable. No screenshots. No sandbox. No drama.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.7 }}
            className="mt-8 flex flex-wrap gap-3"
          >
            <a
              href="#how"
              className="group inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-br from-plasma-500 to-rust-500 text-white font-medium shadow-lg shadow-plasma-500/30 hover:shadow-plasma-500/50 transition"
            >
              See how it works <ArrowRight size={16} className="group-hover:translate-x-1 transition" />
            </a>
            <a
              href="https://github.com/"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-plasma-500/40 bg-ink-900/60 hover:border-plasma-400 hover:bg-plasma-500/10 transition"
            >
              View source
            </a>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="mt-10 flex gap-6 text-xs font-mono text-ink-100/40 tracking-widest"
          >
            <div>NO API KEY</div>
            <div>·</div>
            <div>RUNS LOCALLY</div>
            <div>·</div>
            <div>OPEN CAPABILITIES</div>
          </motion.div>
        </div>

        <div className="relative">
          <Arms />
        </div>
      </div>
    </section>
  );
}
