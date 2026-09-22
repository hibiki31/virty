import { apiClient } from "@/api";
import type { components, paths } from "@/api/openapi";
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

  return requireData(response);
}

export type User = components['schemas']['User'];
export type UserProfile = components['schemas']['UserProfile'];
export type PublicKey = components['schemas']['UserPublickey'];
export type UserAction = 'create' | 'edit' | 'delete' | 'reset';

function requireData<T>(response: { data?: T; error?: unknown }): T {
  if (response.data === undefined) throw response.error;
  return response.data;
}

export async function getUser(username: string): Promise<User> {
  return requireData(await apiClient.GET('/api/users/detail/{username}', { params: { path: { username } } }));
}

export async function getUserScopes(): Promise<string[]> {
  return requireData(await apiClient.GET('/api/users/scopes'));
}

export async function getMyProfile(): Promise<UserProfile> {
  return requireData(await apiClient.GET('/api/users/me'));
}

export async function createUser(body: components['schemas']['UserForCreate']): Promise<User> {
  return requireData(await apiClient.POST('/api/users', { body }));
}

export async function updateUser(username: string, body: components['schemas']['UserForUpdate']): Promise<User> {
  return requireData(await apiClient.PUT('/api/users/{username}', { params: { path: { username } }, body }));
}

export async function deleteUser(username: string): Promise<void> {
  const result = await apiClient.DELETE('/api/users/{username}', { params: { path: { username } } });
  if (!result.response.ok) throw result.error;
}

export async function resetUserPassword(username: string, newPassword: string): Promise<void> {
  const result = await apiClient.PUT('/api/users/{username}/reset-password', {
    params: { path: { username } }, body: { newPassword },
  });
  if (!result.response.ok) throw result.error;
}

export async function updateMyPublickeys(publickeys: PublicKey[]): Promise<UserProfile> {
  return requireData(await apiClient.PUT('/api/users/me/publickeys', { body: { publickeys } }));
}

export async function changeMyPassword(currentPassword: string, newPassword: string): Promise<void> {
  const result = await apiClient.PUT('/api/users/me/password', { body: { currentPassword, newPassword } });
  if (!result.response.ok) throw result.error;
}

export function validNewPassword(value: string): boolean {
  return value.length >= 8 && new TextEncoder().encode(value).length <= 72
    && !/[\s\0]/.test(value)
    && [/[a-z]/, /[A-Z]/, /\d/, /[^A-Za-z0-9]/].every(pattern => pattern.test(value));
}
