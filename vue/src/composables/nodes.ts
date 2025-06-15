import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

export type typeListNode =
  paths["/api/nodes"]["get"]["responses"]["200"]["content"]["application/json"];

export const initNodeList: typeListNode = {
  count: 0,
  data: [],
};

export async function getNode() {
  const res = await apiClient.GET("/api/nodes", {
    params: {
      query: {
        admin: true,
        limit: 100,
      },
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initNodeList;
  }
}
