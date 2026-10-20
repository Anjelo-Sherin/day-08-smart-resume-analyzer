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
        primary: "#D81B60",
        primaryDark: "#AD1457",
        soft: "#FCE4EC",
        blush: "#FFF0F5",
        accent: "#F48FB1",
        accentLight: "#F8BBD0",
        ink: "#4A1A2C",
        muted: "#8E5A70",
      },
      boxShadow: {
        pink: "0 8px 30px rgba(216, 27, 96, 0.12)",
        pinkSm: "0 4px 16px rgba(216, 27, 96, 0.08)",
      },
      borderRadius: {
        card: "16px",
      },
    },
  },
  plugins: [],
};

export default config;
