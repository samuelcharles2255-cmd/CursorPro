import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0a0a0b",
        foreground: "#ededed",
        dark: {
          950: "#070708",
          900: "#0a0a0b",
          850: "#111113",
          800: "#18181b",
          750: "#222226",
          700: "#27272a",
        },
        // Jobs Branch Accent: Navy / Dark Blue
        navy: {
          50: "#f0f5ff",
          100: "#e0ecff",
          200: "#bae6fd",
          400: "#38bdf8",
          500: "#2563eb",
          600: "#1d4ed8",
          700: "#1e40af",
          800: "#1e3a8a",
          900: "#0f172a",
          950: "#0a0f1d",
        },
        // Marketplace Branch Accent: Emerald / Vibrant Green
        market: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
          950: "#022c22",
        },
        // Muted Luxury Gold accents (shared global)
        gold: {
          300: "#f3e5ab",
          400: "#e5c378",
          500: "#d4af37",
          600: "#b89025",
        },
        // P2P Marketplace Light Feed Tokens
        p2p: {
          bg: "#f8fafc",
          surface: "#ffffff",
          muted: "#f1f5f9",
          border: "#e2e8f0",
          text: "#0f172a",
          subtext: "#64748b",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        serif: ["var(--font-cormorant)", "Georgia", "serif"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.45)",
        "glass-sm": "0 4px 16px 0 rgba(0, 0, 0, 0.35)",
        "glass-lg": "0 20px 48px 0 rgba(0, 0, 0, 0.6)",
        "glass-elevated": "0 24px 60px rgba(0, 0, 0, 0.55), inset 0 1px 1px rgba(255, 255, 255, 0.12)",
        "green-glow": "0 0 25px -4px rgba(16, 185, 129, 0.35)",
        "navy-glow": "0 0 25px -4px rgba(37, 99, 235, 0.35)",
        "p2p-card": "0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.06)",
        "p2p-hover": "0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)",
      },
      minHeight: {
        touch: "44px",
      },
      minWidth: {
        touch: "44px",
      },
    },
  },
  plugins: [],
};

export default config;
