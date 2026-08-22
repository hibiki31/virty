import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";
import { toApiPageQuery } from "@/composables/pagination";

export type UserList =
  paths["/api/users"]["get"]["responses"]["200"]["content"]["application/json"];

export type UserListQuery = NonNullable<
  paths["/api/users"]["get"]["parameters"]["query"]
>;

export const initUserList: UserList = {
  count: 0,
  data: [],
};

export async function getUserList(query: UserListQuery): Promise<UserList> {
  const response = await apiClient.GET("/api/users", {
    params: { query: toApiPageQuery(query) },
  });

  return response.data ?? initUserList;
}
