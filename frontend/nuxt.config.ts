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
        { property: 'og:image', content: `${process.env.NUXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'}/onboarding-illust.png?v=2` },
        { name: 'twitter:card', content: 'summary_large_image' },
      ],
      link: [
        {
          rel: 'icon',
          type: 'image/svg+xml',
          href: '/favicon.svg',
        },
        // 폰트 FOUT 방지 — 조선100년체 woff2 미리 다운로드
        {
          rel: 'preload',
          as: 'font',
          type: 'font/woff2',
          href: 'https://gcore.jsdelivr.net/gh/projectnoonnu/noonfonts_2206-02@1.0/ChosunCentennial.woff2',
          crossorigin: '',
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
    // 정적 이미지·폰트 장기 캐싱
    '/*.png':  { headers: { 'cache-control': 'public, max-age=604800, stale-while-revalidate=86400' } },
    '/*.jpg':  { headers: { 'cache-control': 'public, max-age=604800, stale-while-revalidate=86400' } },
    '/*.webp': { headers: { 'cache-control': 'public, max-age=604800, stale-while-revalidate=86400' } },
    '/*.svg':  { headers: { 'cache-control': 'public, max-age=604800, stale-while-revalidate=86400' } },
    '/_nuxt/**': { headers: { 'cache-control': 'public, max-age=31536000, immutable' } },
  },

  typescript: {
    strict: true,
  },
})
