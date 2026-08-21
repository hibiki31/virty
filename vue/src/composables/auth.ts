import { removeCookie, setCookie } from "typescript-cookie";

export function hasAdminScope(scopes: readonly string[]): boolean {
  return scopes.includes("admin");
}

export async function setAxios(accessToken: string) {
  setCookie("accessToken", accessToken);
}

export async function removeAuth() {
  await setAxios("");
  removeCookie("accessToken");
}
