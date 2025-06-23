import { defineStore } from "pinia";
import { jwtDecode } from "jwt-decode";

type JwtPayload = {
  sub: string;
  scopes: ("user" | "admin")[];
  projects: string[];
  exp: number;
};

type AuthState = {
  baseURL: string;
  token: string;
  tokenValidated: boolean;
  authed: boolean;
  scopes: JwtPayload["scopes"];
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
    username: "",
  }),
  actions: {
    loginSuccess(token: string) {
      const decoded = jwtDecode<JwtPayload>(token);
      console.log(decoded);
      this.token = token;
      this.username = decoded.sub;
      this.scopes = decoded.scopes;
      this.tokenValidated = true;
      this.authed = true;
    },
  },
});
