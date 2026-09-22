import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";
import { hasAdminScope } from "@/composables/auth";
import { useAuthStore } from "@/stores/auth";

export type typeListNode =
  paths["/api/nodes"]["get"]["responses"]["200"]["content"]["application/json"];

export const initNodeList: typeListNode = {
  count: 0,
  data: [],
};

export async function getNode(projectId?: string | null) {
  const res = await apiClient.GET("/api/nodes", {
    params: {
      query: {
        admin: !projectId && hasAdminScope(useAuthStore().scopes),
        limit: 100,
        projectId,
      },
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initNodeList;
  }
}

export function getNodeStatusColor(statusCode: string | number) {
  if (statusCode === 10) return "primary";
  else if (statusCode === "init") return "grey lighten-1";
  else if (statusCode === "error") return "red";
  else return "yellow";
}
