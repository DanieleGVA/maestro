import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      colors: {
        maestro: {
          "non-introdotto-bg": "#757575",
          "non-introdotto-fg": "#FFFFFF",
          "non-introdotto-border": "#616161",
          "introdotto-bg": "#FFFFFF",
          "introdotto-fg": "#1A1A1A",
          "introdotto-border": "#616161",
          "lacuna-bg": "#C62828",
          "lacuna-fg": "#FFFFFF",
          "lacuna-border": "#B71C1C",
          "in-recupero-bg": "#EF6C00",
          "in-recupero-fg": "#000000",
          "in-recupero-border": "#E65100",
          "da-consolidare-bg": "#FDD835",
          "da-consolidare-fg": "#000000",
          "da-consolidare-border": "#F9A825",
          "consolidato-bg": "#2E7D32",
          "consolidato-fg": "#FFFFFF",
          "consolidato-border": "#1B5E20",
        },
        focus: "#1565C0",
        page: {
          bg: "#FFFFFF",
          fg: "#1A1A1A",
        },
        surface: {
          bg: "#F5F5F5",
          fg: "#212121",
        },
        border: {
          input: "#616161",
        },
      },
      outline: {
        focus: ["2px solid #1565C0", "2px"],
      },
    },
  },
  plugins: [],
};

export default config;
