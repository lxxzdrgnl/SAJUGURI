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
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000',
    },
  },

  routeRules: {
    '/api/**': { proxy: `${process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000'}/api/**` },
  },

  typescript: {
    strict: true,
  },
})
