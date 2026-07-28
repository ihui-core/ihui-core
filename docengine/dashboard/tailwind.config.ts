import type { Config } from "tailwindcss";
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        border: "var(--color-border)",
        accent: "var(--color-accent)",
        ok: "var(--color-ok)",
        warn: "var(--color-warn)",
        error: "var(--color-error)",
        text: "var(--color-text)",
        muted: "var(--color-muted)",
      },
    },
  },
  plugins: [],
};
export default config;
