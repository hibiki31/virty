import type { paths } from "@/api/openapi";
import createClient, { type Middleware } from "openapi-fetch";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    request.headers.set("Authorization", `Bearer ${authStore.token}`);
    return request;
  },
};

export const apiClient = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_BASE_URL,
});

apiClient.use(authMiddleware);

export type APIClient = typeof apiClient;
