module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        garden: {
          ...require("daisyui/src/theming/themes")["garden"],
          primary: "#2D6A4F",
          "primary-focus": "#1B4332",
          secondary: "#D4A373",
          accent: "#95D5B2",
          neutral: "#2D3436",
          "base-100": "#F5F0EB",
          error: "#C1666B",
          info: "#5B9BD5",
        },
      },
    ],
  },
};
