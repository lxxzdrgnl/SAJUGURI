import type { Config } from 'tailwindcss'

export default {
  content: [
    './components/**/*.{vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.ts',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        night: {
          50:  '#e8e8f0',
          100: '#c5c5d8',
          200: '#9f9fc0',
          300: '#7878a8',
          400: '#5a5a98',
          500: '#3b3b82',
          600: '#2e2e6e',
          700: '#1e1e50',
          800: '#16213e',
          900: '#0f0f1a',
        },
      },
      fontFamily: {
        sans: ['Pretendard', 'Noto Sans KR', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
