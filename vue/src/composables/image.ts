import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

export type typeListImage =
  paths["/api/images"]["get"]["responses"]["200"]["content"]["application/json"];

export const initImageList: typeListImage = {
  count: 0,
  data: [],
};

export async function getImageList(limit = 20, page = 1) {
  const res = await apiClient.GET("/api/images", {
    params: {
      query: {
        page: page - 1,
        admin: true,
        limit: limit,
      },
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initImageList;
  }
}
