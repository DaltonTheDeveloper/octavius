"use client";
import { Github, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative border-t border-plasma-500/10 mt-12">
      <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-ink-100/50">
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 rounded-full bg-gradient-to-br from-plasma-400 to-rust-500" />
          <span className="font-mono tracking-widest">OCTAVIUS</span>
          <span className="text-ink-100/30">·</span>
          <span>local agent control · open capabilities</span>
        </div>
        <div className="flex items-center gap-5">
          <a
            href="https://github.com/DaltonTheDeveloper/octavius"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 hover:text-white transition"
          >
            <Github size={14} /> GitHub
          </a>
          <span className="inline-flex items-center gap-2">
            built with <Heart size={12} className="text-rust-500" /> by Dalton
          </span>
        </div>
      </div>
    </footer>
  );
}
