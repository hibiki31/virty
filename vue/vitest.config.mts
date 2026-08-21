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
    environment: "jsdom",
    include: ["src/**/*.spec.ts"],
    restoreMocks: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary"],
      include: ["src/**/*.{ts,vue}"],
      exclude: [
        // 生成物とtest自身はcoverage対象に含めない。
        "src/**/*.d.ts",
        "src/**/*.spec.ts",
        // application起動時の配線はintegration testの対象とする。
        "src/main.ts",
        "src/plugins/**",
        "src/router/**",
        // 現行画面から未参照で、削除済みaxios adapterへ依存するlegacy SFC。
        "src/components/nodes/NodeRolePatch.vue",
        "src/components/storages/StoragePoolAddDialog.vue",
        "src/components/storages/StoragePoolJoinDialog.vue",
        "src/components/vms/DomainAddTicketsDialog.vue",
        "src/components/vms/DomainGroupPut.vue",
      ],
    },
  },
});
