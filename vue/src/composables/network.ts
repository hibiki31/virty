import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

export type typeListNetwork =
  paths["/api/networks"]["get"]["responses"]["200"]["content"]["application/json"];
export type typeListNetworkQuery = NonNullable<
  paths["/api/networks"]["get"]["parameters"]["query"]
>;

export const initNetworkList: typeListNetwork = {
  count: 0,
  data: [],
};

export async function getNetworkList(query: typeListNetworkQuery) {
  query.page = (query.page || 1) - 1;
  const res = await apiClient.GET("/api/networks", {
    params: {
      query: query,
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initNetworkList;
  }
}
