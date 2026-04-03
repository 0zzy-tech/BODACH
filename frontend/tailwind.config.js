/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        kali: {
          bg:      'var(--kali-bg)',
          surface: 'var(--kali-surface)',
          border:  'var(--kali-border)',
          accent:  'var(--kali-accent)',
          green:   'var(--kali-green)',
          red:     'var(--kali-red)',
          yellow:  'var(--kali-yellow)',
          text:    'var(--kali-text)',
          muted:   'var(--kali-muted)',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
