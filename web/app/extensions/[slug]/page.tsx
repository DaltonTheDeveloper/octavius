import { notFound } from "next/navigation";
import { Download, Sparkles, User2, Tag } from "lucide-react";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { getExtension, accentClasses, parseTags } from "@/lib/extensions";
import { auth, authConfigured } from "@/auth";
import { db } from "@/lib/db";
import ClaimBox from "@/components/ClaimBox";

export const dynamic = "force-dynamic";

export default async function ExtensionPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ code?: string }>;
}) {
  const { slug } = await params;
  const { code } = await searchParams;
  const ext = await getExtension(slug);
  if (!ext) notFound();

  const session = authConfigured ? await auth() : null;
  const userId = session?.user?.email
    ? (await db.user.findUnique({ where: { email: session.user.email } }))?.id
    : undefined;

  const license = userId
    ? await db.license.findUnique({
        where: { userId_extensionId: { userId, extensionId: ext.id } },
      })
    : null;

  const tags = parseTags(ext.tags);
  const autoCode = code && code === ext.membershipCode;

  return (
    <main className="relative min-h-screen">
      <Nav />
      <section className="pt-28 pb-16 px-6 max-w-5xl mx-auto">
        <div className="flex items-start gap-6">
          <div className="h-20 w-20 rounded-2xl bg-ink-900/70 grid place-items-center text-4xl border border-ink-700 flex-shrink-0">
            {ext.iconEmoji}
          </div>
          <div className="flex-1">
            <div className={`inline-flex items-center gap-2 text-xs font-mono tracking-widest px-2 py-1 rounded-full border ${accentClasses(ext.accent)}`}>
              <Tag size={11} /> {ext.tier.toUpperCase()} · BETA
            </div>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight">{ext.name}</h1>
            <p className="mt-2 text-lg text-ink-100/70">{ext.tagline}</p>
            <div className="mt-3 flex items-center gap-4 text-sm text-ink-100/50">
              <span className="inline-flex items-center gap-1.5">
                <User2 size={14} /> @{ext.creator.handle ?? "anon"}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Download size={14} /> {ext.downloads.toLocaleString()} installs
              </span>
            </div>
          </div>
        </div>

        <div className="mt-10 grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <div className="glass rounded-2xl p-6">
              <div className="text-xs font-mono tracking-widest text-plasma-400 mb-3">ABOUT</div>
              <p className="text-ink-100/80 leading-relaxed whitespace-pre-line">{ext.description}</p>
              {tags.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {tags.map((t) => (
                    <span key={t} className="text-xs font-mono text-plasma-300 bg-plasma-500/10 border border-plasma-500/20 px-2 py-1 rounded-md">
                      #{t}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {ext.membershipNote && (
              <div className="glass rounded-2xl p-6 border-rust-500/30">
                <div className="flex items-center gap-2 text-xs font-mono tracking-widest text-rust-400 mb-3">
                  <Sparkles size={12} /> MEMBERSHIP PERK
                </div>
                <p className="text-ink-100/80">{ext.membershipNote}</p>
              </div>
            )}

            <div className="glass rounded-2xl p-6">
              <div className="text-xs font-mono tracking-widest text-plasma-400 mb-3">INSTALL</div>
              <div className="font-mono text-sm bg-ink-950/70 border border-ink-700 rounded-lg p-3 text-plasma-300 overflow-x-auto">
                octavius install {ext.slug}
              </div>
              <div className="mt-3 text-xs text-ink-100/40">
                The daemon fetches the manifest, registers the capabilities, and verifies your license against this site. You'll be asked to sign in on first install.
              </div>
            </div>
          </div>

          <div>
            <ClaimBox
              extensionId={ext.id}
              slug={ext.slug}
              tier={ext.tier}
              hasLicense={!!license}
              licenseSource={license?.source ?? null}
              authConfigured={authConfigured}
              signedIn={!!userId}
              autoCode={autoCode ? code ?? null : null}
            />
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
