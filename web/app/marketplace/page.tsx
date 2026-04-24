import Link from "next/link";
import { Package, Star, Download, Sparkles } from "lucide-react";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { listExtensions, accentClasses, parseTags } from "@/lib/extensions";

export const dynamic = "force-dynamic";

export default async function MarketplacePage() {
  const extensions = await listExtensions();

  return (
    <main className="relative min-h-screen">
      <Nav />
      <section className="pt-28 pb-16 px-6 max-w-6xl mx-auto">
        <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
          MARKETPLACE
        </div>
        <h1 className="text-4xl md:text-5xl font-semibold tracking-tight">
          Install an arm for Claude.
        </h1>
        <p className="mt-3 text-ink-100/60 max-w-2xl">
          Community-built capabilities. All free during beta. Creators can gate
          extensions behind membership codes distributed via YouTube, Patreon,
          Discord — anywhere.
        </p>

        {extensions.length === 0 ? (
          <div className="mt-16 rounded-2xl border border-plasma-500/20 bg-ink-900/50 p-10 text-center">
            <div className="text-ink-100/60 mb-3">
              No extensions published yet.
            </div>
            <div className="text-xs font-mono text-ink-100/40">
              Run <code className="text-plasma-300">npx prisma db push && npx tsx prisma/seed.ts</code>
              {" "}to seed the sample set.
            </div>
          </div>
        ) : (
          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {extensions.map((e) => {
              const tags = parseTags(e.tags);
              return (
                <Link
                  key={e.id}
                  href={`/extensions/${e.slug}`}
                  className={`group rounded-2xl p-5 border bg-ink-900/40 hover:scale-[1.015] hover:bg-ink-900/60 transition ${accentClasses(e.accent).split(" ")[0]}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="h-11 w-11 rounded-xl bg-ink-950/70 grid place-items-center text-xl border border-ink-700">
                        {e.iconEmoji}
                      </div>
                      <div>
                        <div className="font-mono font-semibold text-white">
                          {e.name}
                        </div>
                        <div className="text-xs text-ink-100/50">
                          @{e.creator.handle ?? "anon"}
                        </div>
                      </div>
                    </div>
                    {e.membershipCode && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-mono tracking-widest text-rust-400 border border-rust-500/40 px-2 py-0.5 rounded-full">
                        <Sparkles size={10} /> MEMBERS
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-ink-100/70 line-clamp-2">
                    {e.tagline}
                  </div>
                  <div className="mt-4 flex items-center gap-3 text-xs text-ink-100/40">
                    <span className="inline-flex items-center gap-1">
                      <Download size={11} /> {e.downloads.toLocaleString()}
                    </span>
                    {tags.slice(0, 2).map((t) => (
                      <span key={t} className="text-plasma-400/60 font-mono">
                        #{t}
                      </span>
                    ))}
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </section>
      <Footer />
    </main>
  );
}
