import { apiClient } from "@/api";
import type { paths, components } from "@/api/openapi";
import { toApiPageQuery } from "@/composables/pagination";

export type typeListNetwork =
  paths["/api/networks"]["get"]["responses"]["200"]["content"]["application/json"];
export type typeListNetworkQuery = NonNullable<
  paths["/api/networks"]["get"]["parameters"]["query"]
>;
export type typeCreateNetwork = components["schemas"]["NetworkForCreate"];

export const initNetworkList: typeListNetwork = {
  count: 0,
  data: [],
};

export async function getNetworkList(query: typeListNetworkQuery) {
  const res = await apiClient.GET("/api/networks", {
    params: {
      query: toApiPageQuery(query),
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initNetworkList;
  }
}
