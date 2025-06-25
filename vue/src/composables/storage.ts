import { apiClient } from "@/api";
import type { schemas } from "./schemas";
import type { paths } from "@/api/openapi";

export type typeListStorageQuery = NonNullable<
  paths["/api/storages"]["get"]["parameters"]["query"]
>;

export const initStorageList: schemas["StoragePage"] = {
  count: 0,
  data: [],
};

export function getAvailableColoer(capa: number, available: number) {
  const userd = ((capa - available) / capa) * 100;

  if (userd > 80) return "pink-lighten-2";
  else if (userd > 50) return "yellow-lighten-2";
  else return "teal-lighten-4";
}

export async function getStorageList(query: typeListStorageQuery) {
  query.page = (query.page || 1) - 1;
  const res = await apiClient.GET("/api/storages", {
    params: {
      query: query,
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initStorageList;
  }
}
