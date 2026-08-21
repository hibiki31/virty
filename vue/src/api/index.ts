import type { paths } from "@/api/openapi";
import createClient, { type Middleware } from "openapi-fetch";
import { useAuthStore } from "@/stores/auth";

export function createAuthMiddleware(
  getAccessToken: () => string
): Middleware {
  return {
    async onRequest({ request }) {
      request.headers.set("Authorization", `Bearer ${getAccessToken()}`);
      return request;
    },
  };
}

export const authMiddleware = createAuthMiddleware(
  () => useAuthStore().token
);

export const apiClient = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_BASE_URL,
});

apiClient.use(authMiddleware);

export type APIClient = typeof apiClient;
