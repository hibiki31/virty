import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

export type typeListStorage =
  paths["/api/storages"]["get"]["responses"]["200"]["content"]["application/json"];

export const initStorageList: typeListStorage = {
  count: 0,
  data: [],
};

export async function getStorageList() {
  const res = await apiClient.GET("/api/storages", {
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
    return initStorageList;
  }
}
