import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

export type typeListNetwork =
  paths["/api/networks"]["get"]["responses"]["200"]["content"]["application/json"];

export const initNetworkList: typeListNetwork = {
  count: 0,
  data: [],
};

export async function getNetworkList() {
  const res = await apiClient.GET("/api/networks", {
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
    return initNetworkList;
  }
}
