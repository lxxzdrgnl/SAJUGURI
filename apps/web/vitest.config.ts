import { defineConfig } from 'vitest/config'
export default defineConfig({ esbuild: { jsx: 'automatic' }, test: { include: ['lib/**/*.test.ts', 'components/ui/**/*.test.tsx'] } })
