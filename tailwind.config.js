/** @type {import('tailwindcss').Config} */
const { extendTheme } = require("@chakra-ui/react");

const chakraTheme = extendTheme({
  colors: {
    brand: {
      100: "#7426EF",
      900: "#00C3CC",
    },
  },
  fonts: {
    heading: "Hanken Grotesk, sans-serif",
    body: "Hanken Grotesk, sans-serif",
  },
});

module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: chakraTheme.colors,
    },
  },
};
