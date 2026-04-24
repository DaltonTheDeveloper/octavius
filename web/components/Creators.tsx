"use client";
import { motion } from "framer-motion";
import { Youtube, Link2, Users, Gift, Rotate3d } from "lucide-react";

export default function Creators() {
  return (
    <section id="creators" className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <div className="text-xs font-mono tracking-[0.3em] text-rust-400 mb-3">
            FOR CREATORS
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Reward your YouTube members with real tools.
          </h2>
          <p className="mt-3 text-ink-100/60 max-w-2xl mx-auto">
            Publish an extension. Octavius generates a rotating membership code.
            Share the link in your members-only post. Subscribers get the
            extension free. Everyone else sees it on the marketplace and can
            buy it (when paid tier launches). One flow, any platform.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-4 mb-10">
          {[
            {
              Icon: Users,
              title: "You publish.",
              body: "Upload your extension. Pick a tier (free for now). Octavius auto-generates a secret membership code.",
            },
            {
              Icon: Youtube,
              title: "You share.",
              body: "Drop the member-link in a YouTube Community post for channel members, or Patreon, Discord roles, email — whatever you use.",
            },
            {
              Icon: Gift,
              title: "They claim.",
              body: "Members click, sign in, and get a free license in one tap. Rotate the code anytime to keep the benefit exclusive.",
            },
          ].map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
              className="glass rounded-2xl p-6"
            >
              <div className="h-10 w-10 rounded-xl bg-rust-500/15 border border-rust-500/40 grid place-items-center mb-4">
                <s.Icon size={18} className="text-rust-300" />
              </div>
              <div className="font-semibold text-lg">{s.title}</div>
              <p className="mt-2 text-sm text-ink-100/70">{s.body}</p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="rounded-2xl p-8 md:p-10 bg-gradient-to-br from-rust-500/10 via-ink-800 to-plasma-500/10 border border-rust-500/30"
        >
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <div className="text-xs font-mono tracking-[0.3em] text-rust-400 mb-2">
                THE SHARED LINK
              </div>
              <h3 className="text-2xl font-semibold">
                One URL does it all.
              </h3>
              <p className="mt-3 text-ink-100/70">
                Anyone who visits can <em>see</em> the extension and its value.
                Only people with the code (encoded in the URL, rotatable) can claim
                it for free. Everyone else keeps the page open and buys it when
                they're ready.
              </p>
              <div className="mt-6 inline-flex items-center gap-2 text-xs text-ink-100/50">
                <Rotate3d size={14} /> Creator can rotate the code anytime. Existing licenses stay valid.
              </div>
            </div>
            <div>
              <div className="p-5 rounded-xl bg-ink-950/80 border border-plasma-500/30 font-mono text-xs">
                <div className="flex items-center gap-2 text-ink-100/40 mb-2">
                  <Link2 size={12} /> MEMBER LINK
                </div>
                <div className="text-plasma-300 break-all">
                  getoctavius.vercel.app/extensions/<span className="text-rust-300">cool-ue5-thing</span>?code=<span className="text-emerald-300">8KF2-XJ4D</span>
                </div>
                <div className="mt-4 pt-4 border-t border-ink-700 text-ink-100/50">
                  → opens page<br />
                  → auto-fills code<br />
                  → user signs in<br />
                  → instant free license
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
