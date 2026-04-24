import { Github } from "lucide-react";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { authConfigured, signIn } from "@/auth";

export const dynamic = "force-dynamic";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const { next } = await searchParams;

  async function githubSignIn() {
    "use server";
    await signIn("github", { redirectTo: next ?? "/marketplace" });
  }

  return (
    <main className="relative min-h-screen">
      <Nav />
      <section className="pt-32 pb-20 px-6 max-w-md mx-auto">
        <div className="text-xs font-mono tracking-[0.3em] text-plasma-400 mb-3">
          SIGN IN
        </div>
        <h1 className="text-4xl font-semibold tracking-tight">One arm. One account.</h1>
        <p className="mt-3 text-ink-100/60">
          Free during beta. We track your extension claims so you can install them from any machine.
        </p>

        <div className="mt-10 glass rounded-2xl p-6">
          {authConfigured ? (
            <form action={githubSignIn}>
              <button
                type="submit"
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl py-3 bg-ink-950 border border-plasma-500/40 hover:bg-plasma-500/10 transition font-semibold"
              >
                <Github size={18} /> Continue with GitHub
              </button>
            </form>
          ) : (
            <div className="text-sm text-ink-100/60 leading-relaxed">
              <div className="font-semibold text-rust-400 mb-2">Auth not configured</div>
              <p>To enable GitHub sign-in, set these environment variables:</p>
              <pre className="mt-3 p-3 bg-ink-950 border border-plasma-500/20 rounded-lg text-xs font-mono text-plasma-300 overflow-x-auto">
                AUTH_SECRET=...
                AUTH_GITHUB_ID=...
                AUTH_GITHUB_SECRET=...
              </pre>
              <p className="mt-3 text-xs text-ink-100/40">
                See <code>.env.example</code> for details.
              </p>
            </div>
          )}
        </div>
      </section>
      <Footer />
    </main>
  );
}
