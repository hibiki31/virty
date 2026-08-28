/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from "vue-router/auto";
import { setupLayouts } from "virtual:generated-layouts";
import { routes } from "vue-router/auto-routes";
import { watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { resolveAuthNavigation } from "@/composables/auth";
import { localizedDocumentTitle } from "@/composables/i18n";
import i18n, { type MessageKey } from "@/plugins/i18n";

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

function updateDocumentTitle(): void {
  const titleKey = router.currentRoute.value.meta.titleKey;
  const page = typeof titleKey === "string"
    ? i18n.global.t(titleKey as MessageKey)
    : undefined;
  document.title = localizedDocumentTitle(page);
}

router.afterEach(updateDocumentTitle);
watch(i18n.global.locale, updateDocumentTitle);

export default router;
