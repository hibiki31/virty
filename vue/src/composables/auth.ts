import { removeCookie, setCookie } from "typescript-cookie";

export async function setAxios(accessToken: string) {
  setCookie("accessToken", accessToken);
}

export async function removeAuth() {
  await setAxios("");
  removeCookie("accessToken");
}
