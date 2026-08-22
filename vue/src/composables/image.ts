import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";
import { toApiPageQuery } from "@/composables/pagination";

export type typeListImage =
  paths["/api/images"]["get"]["responses"]["200"]["content"]["application/json"];

export type typeListImageQuery = NonNullable<
  paths["/api/images"]["get"]["parameters"]["query"]
>;

export const initImageList: typeListImage = {
  count: 0,
  data: [],
};

export async function getImageList(query: typeListImageQuery) {
  const res = await apiClient.GET("/api/images", {
    params: { query: toApiPageQuery(query) },
  });
  if (res.data) {
    return res.data;
  } else {
    return initImageList;
  }
}
