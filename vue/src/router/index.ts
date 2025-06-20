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

router.beforeEach((to, from, next) => {
  const auth = useAuthStore();

  console.debug("authed: ", auth.authed, "from: ", from.name, "to: ", to.name);

  // ログインしているのにログインページに行く場合
  if (auth.authed && to.name === "/login") {
    next({
      name: "/login",
    });
  }
  // 認証が必要なページに未認証でアクセスした場合、ログインページは処理しない
  else if (!auth.authed && to.name !== "/login") {
    next({
      name: "/login",
      query: { redirect: to.fullPath },
    });
  }
  // ログイン済み、ログイン不要の場合の通常遷移
  else {
    next();
  }
});

const DEFAULT_TITLE = "Virty Console";
router.afterEach((to, from) => {
  document.title =
    typeof to.meta.title === "string" ? to.meta.title : DEFAULT_TITLE;
});

export default router;
