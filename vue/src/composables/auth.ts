import { removeCookie, setCookie } from "typescript-cookie";
import type { RouteLocationRaw } from "vue-router";

export function hasAdminScope(scopes: readonly string[]): boolean {
  return scopes.includes("admin");
}

export function setAxios(accessToken: string): void {
  setCookie("accessToken", accessToken);
}

export function removeAuth(): void {
  removeCookie("accessToken");
}

type AuthNavigationTarget = {
  fullPath: string;
  path: string;
};

/** 認証状態に応じたrouter guardの遷移先を返す。 */
export function resolveAuthNavigation(
  authed: boolean,
  to: AuthNavigationTarget,
): RouteLocationRaw | undefined {
  if (authed && to.path === "/login") {
    return { path: "/" };
  }

  if (!authed && to.path !== "/login") {
    return {
      path: "/login",
      query: { redirect: to.fullPath },
    };
  }

  return undefined;
}
