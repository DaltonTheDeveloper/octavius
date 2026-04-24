import Link from "next/link";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { auth, authConfigured } from "@/auth";
import { db } from "@/lib/db";
import { Plus, Package, Key } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function Dashboard() {
  const session = authConfigured ? await auth() : null;
  if (!session?.user?.email) {
    return (
      <main className="min-h-screen">
        <Nav />
        <section className="pt-32 px-6 max-w-2xl mx-auto text-center">
          <h1 className="text-3xl font-semibold">Sign in to see your dashboard.</h1>
          <Link
            href="/login?next=/dashboard"
            className="mt-6 inline-block rounded-xl px-5 py-3 bg-gradient-to-br from-plasma-500 to-rust-500 text-white font-semibold"
          >
            Sign in
          </Link>
        </section>
        <Footer />
      </main>
    );
  }

  const user = await db.user.findUnique({
    where: { email: session.user.email },
    include: {
      extensions: { orderBy: { createdAt: "desc" } },
      licenses: { include: { extension: true }, orderBy: { createdAt: "desc" } },
    },
  });

  return (
    <main className="min-h-screen">
      <Nav />
      <section className="pt-28 pb-16 px-6 max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-10">
          <div>
            <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-2">DASHBOARD</div>
            <h1 className="text-3xl font-semibold">Hey, {user?.name ?? user?.handle ?? "friend"}.</h1>
          </div>
          <Link
            href="/dashboard/new"
            className="inline-flex items-center gap-2 rounded-xl px-4 py-2.5 bg-gradient-to-br from-plasma-500 to-rust-500 text-white font-semibold hover:brightness-110"
          >
            <Plus size={16} /> Publish extension
          </Link>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="glass rounded-2xl p-6">
            <div className="flex items-center gap-2 text-xs font-mono tracking-widest text-plasma-400 mb-4">
              <Package size={14} /> YOUR EXTENSIONS
            </div>
            {user?.extensions.length ? (
              <div className="space-y-2">
                {user.extensions.map((e) => (
                  <Link
                    key={e.id}
                    href={`/dashboard/${e.slug}`}
                    className="block rounded-lg p-3 bg-ink-900/40 border border-ink-700 hover:border-plasma-400 transition"
                  >
                    <div className="flex justify-between">
                      <div className="font-semibold">{e.name}</div>
                      <div className="text-xs text-ink-100/40 font-mono">{e.slug}</div>
                    </div>
                    <div className="text-xs text-ink-100/60 mt-1">
                      {e.downloads.toLocaleString()} installs · code: {e.membershipCode ?? "—"}
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-sm text-ink-100/50 italic">
                You haven't published anything yet.
              </div>
            )}
          </div>

          <div className="glass rounded-2xl p-6">
            <div className="flex items-center gap-2 text-xs font-mono tracking-widest text-plasma-400 mb-4">
              <Key size={14} /> YOUR LIBRARY
            </div>
            {user?.licenses.length ? (
              <div className="space-y-2">
                {user.licenses.map((l) => (
                  <div
                    key={l.id}
                    className="flex justify-between items-center rounded-lg p-3 bg-ink-900/40 border border-ink-700"
                  >
                    <div>
                      <div className="font-semibold">{l.extension.name}</div>
                      <div className="text-xs text-ink-100/40 font-mono">
                        {l.source} · {l.extension.slug}
                      </div>
                    </div>
                    <div className="font-mono text-xs text-plasma-300">
                      install
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-ink-100/50 italic">
                No extensions claimed yet. <Link href="/marketplace" className="text-plasma-300 underline">Browse the marketplace</Link>.
              </div>
            )}
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
