// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],

  tailwindcss: {
    config: {
      theme: {
        extend: {
          fontFamily: {
            serif: ['Joseon100Years', 'Noto Serif KR', 'Georgia', 'serif'],
          },
        },
      },
    },
  },

  app: {
    head: {
      title: '사주구리',
      titleTemplate: '%s | 사주구리',
      meta: [
        { name: 'description', content: 'AI가 분석한 나만의 사주 — 오늘의 운세부터 사주 상담까지' },
        { property: 'og:site_name', content: '사주구리' },
        { property: 'og:type', content: 'website' },
        { property: 'og:title', content: '사주구리 — AI 사주 상담' },
        { property: 'og:description', content: 'AI가 분석한 나만의 사주 — 오늘의 운세부터 사주 상담까지' },
        { property: 'og:image', content: `${process.env.NUXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'}/onboarding-illust.png` },
        { name: 'twitter:card', content: 'summary_large_image' },
      ],
      link: [
        {
          rel: 'icon',
          type: 'image/svg+xml',
          href: '/favicon.svg',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&display=swap',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
    },
  },

  routeRules: {
    '/api/**': { proxy: `${process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000'}/api/**` },
  },

  typescript: {
    strict: true,
  },
})
