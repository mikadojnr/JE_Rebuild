/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./templates/**/*.jinja",
    "./templates/**/*.jinja2",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      screens: {
        xs: '475px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography')
  ],
}

