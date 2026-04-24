import { redirect } from "next/navigation";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { auth, authConfigured } from "@/auth";
import { db } from "@/lib/db";
import { randomCode } from "@/lib/ids";

export const dynamic = "force-dynamic";

export default async function NewExtensionPage() {
  const session = authConfigured ? await auth() : null;
  if (!session?.user?.email) redirect("/login?next=/dashboard/new");

  async function publish(formData: FormData) {
    "use server";
    if (!session?.user?.email) throw new Error("unauthenticated");
    const user = await db.user.findUnique({ where: { email: session.user.email } });
    if (!user) throw new Error("no user");

    const slug = String(formData.get("slug") ?? "")
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, "-")
      .replace(/^-+|-+$/g, "");
    if (!slug) throw new Error("slug required");

    const tagsInput = String(formData.get("tags") ?? "")
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    await db.extension.create({
      data: {
        slug,
        name: String(formData.get("name") ?? slug),
        tagline: String(formData.get("tagline") ?? ""),
        description: String(formData.get("description") ?? ""),
        tier: "free",
        accent: String(formData.get("accent") ?? "plasma"),
        iconEmoji: String(formData.get("iconEmoji") ?? "✦"),
        tags: JSON.stringify(tagsInput),
        creatorId: user.id,
        membershipCode: formData.get("enableMembership") === "on" ? randomCode() : null,
        membershipNote: String(formData.get("membershipNote") ?? "") || null,
      },
    });

    await db.user.update({ where: { id: user.id }, data: { isCreator: true } });
    redirect(`/dashboard/${slug}`);
  }

  return (
    <main className="min-h-screen">
      <Nav />
      <section className="pt-28 pb-16 px-6 max-w-2xl mx-auto">
        <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">PUBLISH</div>
        <h1 className="text-3xl font-semibold mb-8">New extension</h1>
        <form action={publish} className="space-y-5">
          <Field label="Slug" name="slug" placeholder="my-cool-thing" required />
          <Field label="Name" name="name" placeholder="My Cool Thing" required />
          <Field label="Tagline" name="tagline" placeholder="One-line description" required />
          <Textarea label="Description" name="description" placeholder="Longer description, markdown-ish." />
          <Field label="Tags (comma-separated)" name="tags" placeholder="blender, vfx" />
          <div className="grid grid-cols-2 gap-4">
            <Field label="Icon emoji" name="iconEmoji" placeholder="🧊" />
            <div>
              <label className="text-xs font-mono tracking-widest text-ink-100/60 uppercase">Accent</label>
              <select name="accent" defaultValue="plasma" className="mt-1 w-full rounded-lg bg-ink-950/70 border border-plasma-500/30 px-3 py-2">
                <option value="plasma">Plasma</option>
                <option value="rust">Rust</option>
                <option value="chrome">Chrome</option>
              </select>
            </div>
          </div>

          <div className="rounded-xl border border-rust-500/30 bg-rust-500/5 p-4 space-y-3">
            <div className="flex items-center gap-2">
              <input type="checkbox" name="enableMembership" id="em" defaultChecked className="accent-rust-500" />
              <label htmlFor="em" className="font-semibold text-rust-300">Enable membership code</label>
            </div>
            <p className="text-xs text-ink-100/60 leading-relaxed">
              Generate a secret code you can share with YouTube members, Patreon supporters, etc. Holders claim this extension for free. Everyone else can still buy it (when paid tier launches) or see it listed.
            </p>
            <Textarea
              label="Note shown on the listing"
              name="membershipNote"
              placeholder="e.g. Join my YouTube members to get the monthly code."
            />
          </div>

          <button className="w-full rounded-xl py-3 bg-gradient-to-br from-plasma-500 to-rust-500 text-white font-semibold hover:brightness-110">
            Publish
          </button>
        </form>
      </section>
      <Footer />
    </main>
  );
}

function Field(props: { label: string; name: string; placeholder?: string; required?: boolean }) {
  return (
    <div>
      <label className="text-xs font-mono tracking-widest text-ink-100/60 uppercase">{props.label}</label>
      <input
        name={props.name}
        placeholder={props.placeholder}
        required={props.required}
        className="mt-1 w-full rounded-lg bg-ink-950/70 border border-plasma-500/30 px-3 py-2 focus:outline-none focus:border-plasma-400"
      />
    </div>
  );
}

function Textarea(props: { label: string; name: string; placeholder?: string }) {
  return (
    <div>
      <label className="text-xs font-mono tracking-widest text-ink-100/60 uppercase">{props.label}</label>
      <textarea
        name={props.name}
        placeholder={props.placeholder}
        rows={4}
        className="mt-1 w-full rounded-lg bg-ink-950/70 border border-plasma-500/30 px-3 py-2 focus:outline-none focus:border-plasma-400"
      />
    </div>
  );
}
