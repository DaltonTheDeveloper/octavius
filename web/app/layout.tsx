import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Octavius — eight arms for Claude",
  description:
    "A local host bus that gives Claude structured, reversible access to your whole machine. Named after Doc Ock — more arms means more work, without the insanity.",
  openGraph: {
    title: "Octavius — eight arms for Claude",
    description:
      "Live machine graph. One-click approvals. Reversible by default. Personal AI agent control for your real desktop.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased font-display">
        {children}
      </body>
    </html>
  );
}
