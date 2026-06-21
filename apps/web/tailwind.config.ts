import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#07090d",
          900: "#0b0f16",
          850: "#101620",
          800: "#151c28",
          700: "#222b38",
        },
        signal: {
          ok: "#34d399",
          warn: "#fbbf24",
          error: "#f87171",
          cyan: "#67e8f9",
        },
      },
      boxShadow: {
        panel: "0 20px 80px rgb(0 0 0 / 0.28)",
      },
    },
  },
  plugins: [],
};

export default config;
