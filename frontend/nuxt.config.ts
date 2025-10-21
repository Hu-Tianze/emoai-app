// / <reference types="node" />
// https://nuxt.com/docs/api/configuration/nuxt-config
import { defineNuxtConfig } from 'nuxt/config';

export default defineNuxtConfig({
  srcDir: 'src/',
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@pinia/nuxt',
  ],

  // 构建配置
  build: {
    transpile: ['@nuxt/ui', 'tailwindcss'],
  },

  app: {
    head: {
      title: 'EmoAI - AI Emotional Companion',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI Emotional Companion - Chat with AI friends' },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  // 环境变量
  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:3000',
      requestTimeout: process.env.NUXT_PUBLIC_REQUEST_TIMEOUT || '30000',
    },
  },

  experimental: {
    viewTransition: true,
  },

  compatibilityDate: '2024-10-18',

  // Vite 构建配置 - 防止EMFILE错误
  vite: {
    define: {
      __DEV__: process.env.NODE_ENV === 'development',
    },
    server: {
      watch: {
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/.nuxt/**',
          '**/.bun/**',
          '**/dist/**',
          '**/chat/**',
          '**/.next/**',
        ],
      },
      fs: {
        strict: false,
      },
    },
    // 修复 Tailwind CSS ESM 导入问题
    ssr: {
      external: ['tailwindcss'],
    },
  },

  // Nitro 服务器配置
  nitro: {
    prerender: {
      ignore: ['/api'],
      crawlLinks: false,
    },
  },
});
