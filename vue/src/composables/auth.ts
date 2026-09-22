import { removeCookie, setCookie } from "typescript-cookie";
import type { RouteLocationRaw } from "vue-router";

export function hasAdminScope(scopes: readonly string[]): boolean {
  return scopes.includes("admin");
}

const LEGACY_USER_SCOPES = new Set([
  "inventory.read",
  "vm.read",
  "vm.power",
  "node.read",
  "storage.read",
  "image.read",
  "network.read",
  "project.read",
  "flavor.read",
  "task.read.self",
]);

/** APIと同じ後方互換・namespace wildcard規則でscopeを判定する。 */
export function hasScope(
  scopes: readonly string[],
  requiredScope: string,
): boolean {
  return scopes.some((scope) =>
    scope === "admin" ||
    scope === requiredScope ||
    (scope === "user" && LEGACY_USER_SCOPES.has(requiredScope)) ||
    (scope.endsWith(".*") && requiredScope.startsWith(`${scope.slice(0, -2)}.`)),
  );
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
  requiresAdmin?: boolean;
};

/** 認証状態と管理者限定metaに応じたrouter guardの遷移先を返す。 */
export function resolveAuthNavigation(
  authed: boolean,
  to: AuthNavigationTarget,
  scopes: readonly string[] = [],
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

  if (to.requiresAdmin === true && !hasAdminScope(scopes)) {
    return { path: "/" };
  }

  return undefined;
}
