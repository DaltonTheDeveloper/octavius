"use client";
import { Github } from "lucide-react";
import Link from "next/link";

export default function Nav() {
  return (
    <nav className="fixed top-0 inset-x-0 z-50 backdrop-blur-md bg-ink-950/60 border-b border-plasma-500/10">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="relative flex h-7 w-7">
            <span className="animate-ping absolute inset-0 rounded-full bg-plasma-500/40" />
            <span className="relative h-7 w-7 rounded-full bg-gradient-to-br from-plasma-400 to-rust-500 ring-1 ring-plasma-300/40" />
          </span>
          <span className="font-mono tracking-[0.25em] text-sm group-hover:text-plasma-300 transition">
            OCTAVIUS
          </span>
        </Link>
        <div className="hidden sm:flex items-center gap-6 text-sm text-ink-100/70">
          <Link href="/marketplace" className="hover:text-white transition">Marketplace</Link>
          <Link href="/#creators" className="hover:text-white transition">Creators</Link>
          <Link href="/dashboard" className="hover:text-white transition">Dashboard</Link>
          <Link href="/#how" className="hover:text-white transition">How it works</Link>
        </div>
        <a
          href="https://github.com/DaltonTheDeveloper/octavius"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 text-sm rounded-lg px-3 py-1.5 border border-plasma-500/30 hover:border-plasma-400 hover:bg-plasma-500/10 transition"
        >
          <Github size={14} /> GitHub
        </a>
      </div>
    </nav>
  );
}
