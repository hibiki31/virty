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
  scopes: JwtPayload["scopes"];
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
    scopes: [],
    projects: [],
    username: "",
  }),
  actions: {
    loginSuccess(token: string) {
      const decoded = jwtDecode<JwtPayload>(token);
      this.token = token;
      this.username = decoded.sub;
      this.scopes = decoded.scopes ?? [];
      this.projects = decoded.projects ?? [];
      this.tokenValidated = true;
      this.authed = true;
    },
    loginFailure() {
      this.token = "";
      this.username = "";
      this.scopes = [];
      this.projects = [];
      this.tokenValidated = true;
      this.authed = false;
    },
  },
});
