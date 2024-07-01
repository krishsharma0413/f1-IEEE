/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html"],
  theme: {
    extend: {
      colors:{
        "bg": "#ebebe4",
        "text": "#2f2f2f",
        "accent": "#f10f10"
      },
      // Nulshock Rg font
      fontFamily: {
        'nulshock': ['NulshockRg-Bold', 'sans-serif']
      },
    },
  },
  plugins: [],
}

