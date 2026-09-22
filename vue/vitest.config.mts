import Vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import VueRouter from "unplugin-vue-router/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    VueRouter({ dts: false }),
    Vue(),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("src", import.meta.url)),
    },
  },
  test: {
    clearMocks: true,
    // 並行するworktree検証やimage buildとのCPU競合を抑える。
    maxWorkers: 2,
    environment: "jsdom",
    include: ["src/**/*.spec.ts", "e2e/**/*.unit.ts"],
    restoreMocks: true,
    setupFiles: ["src/__tests__/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary"],
      include: ["src/**/*.{ts,vue}"],
      thresholds: {
        "src/composables/auth.ts": {
          branches: 80,
          functions: 80,
          lines: 90,
          statements: 90,
        },
        "src/composables/notify.ts": {
          branches: 80,
          functions: 80,
          lines: 90,
          statements: 90,
        },
        "src/composables/pagination.ts": {
          branches: 80,
          functions: 80,
          lines: 90,
          statements: 90,
        },
        "src/composables/projectFilter.ts": {
          branches: 80,
          functions: 80,
          lines: 90,
          statements: 90,
        },
        "src/composables/taskPolling.ts": {
          branches: 80,
          functions: 80,
          lines: 90,
          statements: 90,
        },
      },
      exclude: [
        // 生成物とtest自身はcoverage対象に含めない。
        "src/**/*.d.ts",
        "src/**/*.spec.ts",
        // application起動時の配線はintegration testの対象とする。
        "src/main.ts",
        "src/plugins/**",
        "src/router/**",
      ],
    },
  },
});
