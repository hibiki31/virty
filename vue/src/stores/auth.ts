import { defineStore } from "pinia";
import { jwtDecode } from "jwt-decode";

type JwtPayload = {
  sub: string;
  scopes: string[];
  projects: string[];
  exp: number;
};

type AuthState = {
  baseURL: string;
  token: string;
  tokenValidated: boolean;
  authed: boolean;
  grantedScopes: JwtPayload["scopes"];
  adminMode: boolean;
  projects: JwtPayload["projects"];
  username: string;
};

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    baseURL: [null, undefined].includes(import.meta.env.VITE_API_BASE_URL)
      ? ""
      : import.meta.env.VITE_API_BASE_URL,
    token: "",
    tokenValidated: false,
    authed: false,
    grantedScopes: [],
    adminMode: false,
    projects: [],
    username: "",
  }),
  getters: {
    canUseAdminMode: (state): boolean => state.grantedScopes.includes("admin"),
    // 一般モードでは包括的な管理権限を使わず、通常参照と個別に付与されたscopeを使う。
    scopes: (state): string[] => state.grantedScopes.flatMap(scope =>
      scope === "admin" && !state.adminMode ? ["user"] : [scope],
    ),
  },
  actions: {
    setAdminMode(enabled: boolean) {
      this.adminMode = enabled && this.canUseAdminMode;
      try {
        if (this.adminMode) sessionStorage.setItem("virty:admin-mode", this.username);
        else sessionStorage.removeItem("virty:admin-mode");
      } catch {
        // 保存できない環境では再読込後に一般モードへ戻す。
        this.adminMode = false;
      }
    },
    loginSuccess(token: string, restoreMode = false) {
      const decoded = jwtDecode<JwtPayload>(token);
      this.token = token;
      this.username = decoded.sub;
      this.grantedScopes = decoded.scopes ?? [];
      this.projects = decoded.projects ?? [];
      this.tokenValidated = true;
      this.authed = true;
      let savedMode = false;
      try {
        savedMode = restoreMode && sessionStorage.getItem("virty:admin-mode") === this.username;
      } catch {
        // sessionStorageが利用できなければ一般モードで開始する。
      }
      this.setAdminMode(savedMode);
    },
    loginFailure() {
      this.token = "";
      this.username = "";
      this.grantedScopes = [];
      this.setAdminMode(false);
      this.projects = [];
      this.tokenValidated = true;
      this.authed = false;
    },
  },
});
