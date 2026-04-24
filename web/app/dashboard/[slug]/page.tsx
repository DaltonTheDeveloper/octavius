import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { auth, authConfigured } from "@/auth";
import { db } from "@/lib/db";
import { randomCode } from "@/lib/ids";
import { revalidatePath } from "next/cache";

export const dynamic = "force-dynamic";

export default async function ExtensionAdmin({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const session = authConfigured ? await auth() : null;
  if (!session?.user?.email) redirect("/login");

  const user = await db.user.findUnique({ where: { email: session.user.email } });
  if (!user) redirect("/login");

  const ext = await db.extension.findUnique({
    where: { slug },
    include: { redemptions: { include: { user: true }, orderBy: { createdAt: "desc" } } },
  });
  if (!ext || ext.creatorId !== user.id) notFound();

  async function rotateCode() {
    "use server";
    const newCode = randomCode();
    await db.extension.update({ where: { id: ext!.id }, data: { membershipCode: newCode } });
    revalidatePath(`/dashboard/${ext!.slug}`);
  }

  async function clearCode() {
    "use server";
    await db.extension.update({ where: { id: ext!.id }, data: { membershipCode: null } });
    revalidatePath(`/dashboard/${ext!.slug}`);
  }

  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://getoctavius.vercel.app";
  const memberLink = ext.membershipCode
    ? `${baseUrl}/extensions/${ext.slug}?code=${ext.membershipCode}`
    : null;

  return (
    <main className="min-h-screen">
      <Nav />
      <section className="pt-28 pb-16 px-6 max-w-4xl mx-auto">
        <Link href="/dashboard" className="text-xs font-mono text-plasma-400 hover:text-plasma-300">← dashboard</Link>
        <h1 className="mt-3 text-3xl font-semibold">{ext.name}</h1>
        <div className="text-sm text-ink-100/50 font-mono">{ext.slug}</div>

        <div className="mt-8 grid md:grid-cols-2 gap-6">
          <div className="glass rounded-2xl p-6 space-y-4">
            <div className="text-xs font-mono tracking-widest text-plasma-400">MEMBERSHIP CODE</div>
            {ext.membershipCode ? (
              <>
                <div className="p-4 rounded-lg bg-ink-950/70 border border-rust-500/40 font-mono text-xl text-rust-300 tracking-[0.3em] text-center">
                  {ext.membershipCode}
                </div>
                <div>
                  <div className="text-xs text-ink-100/50 mb-1">Shareable member link:</div>
                  <div className="p-2 rounded-lg bg-ink-950/70 border border-ink-700 font-mono text-xs break-all">
                    {memberLink}
                  </div>
                </div>
                <p className="text-xs text-ink-100/50 leading-relaxed">
                  Post this link in your YouTube members-only post, Patreon, Discord role channel, or email list.
                  Anyone who clicks + signs in gets this extension for free.
                </p>
                <div className="flex gap-2">
                  <form action={rotateCode} className="flex-1">
                    <button className="w-full rounded-lg py-2 bg-rust-500/15 border border-rust-500/40 text-rust-300 font-semibold hover:bg-rust-500/25 transition">
                      Rotate code
                    </button>
                  </form>
                  <form action={clearCode} className="flex-1">
                    <button className="w-full rounded-lg py-2 bg-ink-900 border border-ink-700 text-ink-100/70 hover:border-rust-500/40 transition">
                      Disable
                    </button>
                  </form>
                </div>
                <div className="text-[11px] text-ink-100/40">
                  Rotating invalidates the old link for anyone who hasn't redeemed. Existing licenses keep working.
                </div>
              </>
            ) : (
              <>
                <p className="text-sm text-ink-100/60">No code active. Anyone can still claim this extension during beta — the code gates value when you flip it to paid.</p>
                <form action={rotateCode}>
                  <button className="w-full rounded-lg py-2.5 bg-rust-500/15 border border-rust-500/40 text-rust-300 font-semibold">
                    Generate code
                  </button>
                </form>
              </>
            )}
          </div>

          <div className="glass rounded-2xl p-6">
            <div className="text-xs font-mono tracking-widest text-plasma-400 mb-4">REDEMPTIONS</div>
            {ext.redemptions.length === 0 ? (
              <div className="text-sm text-ink-100/50 italic">No redemptions yet.</div>
            ) : (
              <div className="space-y-2">
                {ext.redemptions.map((r) => (
                  <div key={r.id} className="flex justify-between p-3 rounded-lg bg-ink-900/40 border border-ink-700 text-sm">
                    <span>{r.user.name ?? r.user.handle ?? r.user.email}</span>
                    <span className="font-mono text-ink-100/40 text-xs">
                      {new Date(r.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-4 text-xs text-ink-100/40">
              Total installs: <span className="text-plasma-300 font-mono">{ext.downloads.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
