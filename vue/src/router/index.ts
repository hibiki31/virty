/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from "vue-router/auto";
import { setupLayouts } from "virtual:generated-layouts";
import { routes } from "vue-router/auto-routes";
import { useAuthStore } from "@/stores/auth";
import { resolveAuthNavigation } from "@/composables/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: setupLayouts(routes),
});

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.("Failed to fetch dynamically imported module")) {
    if (localStorage.getItem("vuetify:dynamic-reload")) {
      console.error("Dynamic import error, reloading page did not fix it", err);
    } else {
      console.log("Reloading page to fix dynamic import error");
      localStorage.setItem("vuetify:dynamic-reload", "true");
      location.assign(to.fullPath);
    }
  } else {
    console.error(err);
  }
});

router.isReady().then(() => {
  localStorage.removeItem("vuetify:dynamic-reload");
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  return resolveAuthNavigation(
    auth.authed,
    {
      fullPath: to.fullPath,
      path: to.path,
      requiresAdmin: to.meta.requiresAdmin === true,
    },
    auth.scopes,
  );
});

const DEFAULT_TITLE = "Virty Console";
router.afterEach((to) => {
  document.title =
    typeof to.meta.title === "string" ? to.meta.title : DEFAULT_TITLE;
});

export default router;
