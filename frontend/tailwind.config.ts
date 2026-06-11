import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1e1b4b",
        muted: "#5b5877",
        canvas: "#faf9ff",
        panel: "#ffffff",
        primary: {
          50: "#f5f3ff",
          100: "#ede9fe",
          500: "#7c3aed",
          600: "#6d28d9",
          700: "#5b21b6"
        },
        accent: {
          50: "#ecfeff",
          500: "#0891b2",
          600: "#0e7490"
        }
      },
      boxShadow: {
        soft: "0 18px 50px -28px rgba(46, 16, 101, 0.28)",
        card: "0 8px 30px -20px rgba(46, 16, 101, 0.22)"
      },
      fontFamily: {
        heading: ['"Be Vietnam Pro"', '"Noto Sans"', "sans-serif"],
        sans: ['"Noto Sans"', '"Be Vietnam Pro"', "sans-serif"]
      },
      keyframes: {
        pulseSoft: {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "1" }
        }
      },
      animation: {
        "pulse-soft": "pulseSoft 1.3s ease-in-out infinite"
      }
    }
  },
  plugins: []
} satisfies Config;

