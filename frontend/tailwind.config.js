/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        muted: "#667085",
        line: "#D7DEE8",
        panel: "#F7F9FC",
        brand: "#1F7A6D",
        accent: "#B24C2E"
      },
      boxShadow: {
        soft: "0 16px 40px rgba(23, 32, 51, 0.08)"
      }
    },
  },
  plugins: [],
};
