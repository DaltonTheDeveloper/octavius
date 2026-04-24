"use client";
import { motion } from "framer-motion";

export default function About() {
  return (
    <section id="about" className="relative py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="rounded-3xl p-10 md:p-14 bg-gradient-to-br from-ink-900 via-ink-800 to-ink-900 border border-plasma-500/20 relative overflow-hidden"
        >
          <div className="absolute -top-20 -right-20 h-80 w-80 rounded-full bg-plasma-500/10 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-20 -left-20 h-80 w-80 rounded-full bg-rust-500/10 blur-3xl pointer-events-none" />

          <div className="relative">
            <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-4">
              WHY "OCTAVIUS"
            </div>
            <h2 className="text-3xl md:text-5xl font-semibold tracking-tight leading-tight">
              Named after Otto Octavius.
            </h2>
            <p className="mt-6 text-lg text-ink-100/80 leading-relaxed max-w-3xl">
              In Spider-Man, Doctor Octopus could only outpace human limits
              because he had four extra mechanical arms — each independently
              skilled, each extending his reach. The catch: the arms started
              running him.
            </p>
            <p className="mt-4 text-lg text-ink-100/80 leading-relaxed max-w-3xl">
              <span className="text-plasma-300 font-semibold">Octavius gives Claude that same multiplier — without the takeover.</span> {" "}
              The arms are capabilities. The neural inhibitor is the approval
              bus and the journal. You stay the brain. Claude gets the reach.
              Nothing happens to your machine that you didn't see and approve,
              and nothing that's done can't be undone.
            </p>

            <div className="mt-8 grid sm:grid-cols-3 gap-4">
              {[
                { k: "More arms", v: "Each capability is a new reach. Add one in ~30 lines." },
                { k: "Same brain", v: "You hold the approval bus. Claude proposes; you decide." },
                { k: "No insanity", v: "Append-only journal with inverse ops. One key undoes everything." },
              ].map((x) => (
                <div
                  key={x.k}
                  className="rounded-xl p-4 bg-ink-900/50 border border-plasma-500/20"
                >
                  <div className="text-plasma-300 font-semibold">{x.k}</div>
                  <div className="text-sm text-ink-100/70 mt-1">{x.v}</div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
