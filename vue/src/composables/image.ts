import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

export type typeListImage =
  paths["/api/images"]["get"]["responses"]["200"]["content"]["application/json"];

export const initImageList: typeListImage = {
  count: 0,
  data: [],
};

export async function getImageList() {
  const res = await apiClient.GET("/api/images", {
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
    return initImageList;
  }
}
