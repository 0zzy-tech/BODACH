/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        kali: {
          bg: '#0d1117',
          surface: '#161b22',
          border: '#30363d',
          accent: '#58a6ff',
          green: '#3fb950',
          red: '#f85149',
          yellow: '#d29922',
          text: '#e6edf3',
          muted: '#8b949e',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
