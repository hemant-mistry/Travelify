/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{html,js,jsx}",
    "./node_modules/react-tailwindcss-datepicker/dist/index.esm.js",
  ],
  theme: {
    extend: {
      colors: {
        "custom-gray": "#A9A9A9",
        "custom-blue": "#2D63D8",
        "custom-light-blue": "#40A9EB",
      },
      fontFamily: {
        lato: ["Lato", "sans-serif"],
      },
    },
  },
  // eslint-disable-next-line no-undef
  plugins: [require("daisyui")],
};
