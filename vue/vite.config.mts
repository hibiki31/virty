// Plugins
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import Fonts from "unplugin-fonts/vite";
import Layouts from "vite-plugin-vue-layouts-next";
import Vue from "@vitejs/plugin-vue";
import VueRouter from "unplugin-vue-router/vite";
import { VueRouterAutoImports } from "unplugin-vue-router";
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify";

// Utilities
import { defineConfig, loadEnv } from "vite";
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const {
    VITE_DEV_API_PROXY_TARGET: apiProxyTarget,
    VITE_DEV_NOVNC_PROXY_TARGET: noVncProxyTarget,
  } = loadEnv(mode, process.cwd(), "");
  const generateDts = command === "build";
  const appVersion = process.env.npm_package_version ?? "unknown";

  return {
    plugins: [
      VueRouter({
        dts: generateDts ? "src/typed-router.d.ts" : false,
      }),
      Layouts(),
      AutoImport({
        imports: [
          "vue",
          VueRouterAutoImports,
          {
            pinia: ["defineStore", "storeToRefs"],
          },
          {
            "@/composables/rules.ts": [["default", "r"]],
          },
          {
            "@/composables/trigger.ts": [
              ["useReloadListener", "useReloadListener"],
            ],
          },
        ],
        dirs: ["src/stores"],
        dts: generateDts ? "src/auto-imports.d.ts" : false,
        vueTemplate: true,
      }),
      Components({
        dts: generateDts ? "src/components.d.ts" : false,
      }),
      Vue({
        template: { transformAssetUrls },
      }),
      // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
      Vuetify({
        autoImport: true,
        styles: {
          configFile: "src/styles/settings.scss",
        },
      }),
      Fonts({
        fontsource: {
          families: [
            {
              name: "Roboto",
              weights: [100, 300, 400, 500, 700, 900],
              styles: ["normal", "italic"],
            },
          ],
        },
      }),
    ],
    optimizeDeps: {
      exclude: [
        "vuetify",
        "vue-router",
        "unplugin-vue-router/runtime",
        "unplugin-vue-router/data-loaders",
        "unplugin-vue-router/data-loaders/basic",
      ],
    },
    define: {
      "process.env": {},
      "import.meta.env.VITE_APP_VERSION": JSON.stringify(appVersion),
    },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("src", import.meta.url)),
      },
      extensions: [".js", ".json", ".jsx", ".mjs", ".ts", ".tsx", ".vue"],
    },
    server: {
      port: 3000,
      host: "0.0.0.0",
      proxy: apiProxyTarget || noVncProxyTarget
        ? {
            ...(apiProxyTarget
              ? {
                  "/api": {
                    target: apiProxyTarget,
                    changeOrigin: true,
                  },
                }
              : {}),
            ...(noVncProxyTarget
              ? {
                  "/novnc": {
                    target: noVncProxyTarget,
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/novnc/, ""),
                    ws: true,
                  },
                }
              : {}),
          }
        : undefined,
    },
    css: {
      preprocessorOptions: {
        sass: {
          api: "modern-compiler",
        },
        scss: {
          api: "modern-compiler",
        },
      },
    },
  };
});
