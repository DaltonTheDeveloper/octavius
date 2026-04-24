import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#06070b",
          900: "#0b0d14",
          800: "#11141d",
          700: "#1a1e2b",
          600: "#262b3c",
        },
        rust: {
          400: "#fb923c",
          500: "#f97316",
          600: "#ea580c",
        },
        plasma: {
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
        },
        chrome: {
          400: "#67e8f9",
          500: "#22d3ee",
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
        display: ["var(--font-display)", "ui-sans-serif", "system-ui"],
      },
      animation: {
        "pulse-slow": "pulse 4s ease-in-out infinite",
        "tentacle-1": "tentacle 6s ease-in-out infinite",
        "tentacle-2": "tentacle 7s ease-in-out infinite -1s",
        "tentacle-3": "tentacle 8s ease-in-out infinite -2s",
        "tentacle-4": "tentacle 9s ease-in-out infinite -3s",
        "scan": "scan 8s linear infinite",
        "float": "float 8s ease-in-out infinite",
      },
      keyframes: {
        tentacle: {
          "0%, 100%": { transform: "rotate(0deg)" },
          "50%": { transform: "rotate(6deg)" },
        },
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-12px)" },
        },
      },
      backgroundImage: {
        "grid":
          "linear-gradient(to right, rgba(168,85,247,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(168,85,247,0.06) 1px, transparent 1px)",
        "radial-glow":
          "radial-gradient(circle at 50% 0%, rgba(168,85,247,0.18), transparent 60%)",
      },
    },
  },
  plugins: [],
};
export default config;
