import { apiClient } from "@/api";
import type { components, paths } from "@/api/openapi";
import { toApiPageQuery } from "@/composables/pagination";

export type ProjectSummary = components["schemas"]["ProjectSummary"];
export type ProjectDetail = components["schemas"]["ProjectDetail"];
export type ProjectForCreate = components["schemas"]["ProjectForCreate"];
export type ProjectForNameUpdate =
  components["schemas"]["ProjectForNameUpdate"];
export type ProjectResourceGrantsUpdate =
  components["schemas"]["ProjectResourceGrantsUpdate"];
export type ProjectResourceGrantCandidates =
  components["schemas"]["ProjectResourceGrantCandidates"];
export type ProjectPage =
  paths["/api/projects"]["get"]["responses"]["200"]["content"]["application/json"];
export type ProjectListQuery = NonNullable<
  paths["/api/projects"]["get"]["parameters"]["query"]
>;
export type ProjectMemberCandidatePage =
  paths["/api/projects/{project_id}/member-candidates"]["get"]["responses"]["200"]["content"]["application/json"];
export type ProjectMemberCandidateQuery = NonNullable<
  paths["/api/projects/{project_id}/member-candidates"]["get"]["parameters"]["query"]
>;

export const initProjectPage: ProjectPage = { count: 0, data: [] };

function requireData<T>(data: T | undefined, error: unknown): T {
  if (data === undefined) {
    throw error;
  }
  return data;
}

export async function getProjectList(
  query: ProjectListQuery,
): Promise<ProjectPage> {
  const response = await apiClient.GET("/api/projects", {
    params: { query: toApiPageQuery(query) },
  });
  return response.data ?? initProjectPage;
}

export async function getProject(projectId: string): Promise<ProjectDetail> {
  const response = await apiClient.GET("/api/projects/{project_id}", {
    params: { path: { project_id: projectId } },
  });
  return requireData(response.data, response.error);
}

export async function createProject(body: ProjectForCreate) {
  const response = await apiClient.POST("/api/tasks/projects", { body });
  return requireData(
    response.data as components["schemas"]["Task"][] | undefined,
    response.error,
  );
}

export async function updateProjectName(
  projectId: string,
  body: ProjectForNameUpdate,
): Promise<ProjectDetail> {
  const response = await apiClient.PATCH("/api/projects/{project_id}", {
    params: { path: { project_id: projectId } },
    body,
  });
  return requireData(response.data, response.error);
}

export async function getProjectMemberCandidates(
  projectId: string,
  query: ProjectMemberCandidateQuery,
): Promise<ProjectMemberCandidatePage> {
  const response = await apiClient.GET(
    "/api/projects/{project_id}/member-candidates",
    {
      params: {
        path: { project_id: projectId },
        query: toApiPageQuery(query),
      },
    },
  );
  return requireData(response.data, response.error);
}

export async function addProjectMember(
  projectId: string,
  username: string,
): Promise<ProjectDetail> {
  const response = await apiClient.PUT(
    "/api/projects/{project_id}/members/{username}",
    { params: { path: { project_id: projectId, username } } },
  );
  return requireData(response.data, response.error);
}

export async function removeProjectMember(
  projectId: string,
  username: string,
): Promise<ProjectDetail> {
  const response = await apiClient.DELETE(
    "/api/projects/{project_id}/members/{username}",
    { params: { path: { project_id: projectId, username } } },
  );
  return requireData(response.data, response.error);
}

export async function replaceProjectResourceGrants(
  projectId: string,
  body: ProjectResourceGrantsUpdate,
): Promise<ProjectDetail> {
  const response = await apiClient.PUT(
    "/api/projects/{project_id}/resource-grants",
    {
      params: { path: { project_id: projectId } },
      body,
    },
  );
  return requireData(response.data, response.error);
}

export async function getProjectResourceGrantCandidates(
  projectId: string,
): Promise<ProjectResourceGrantCandidates> {
  const response = await apiClient.GET(
    "/api/projects/{project_id}/resource-grant-candidates",
    { params: { path: { project_id: projectId } } },
  );
  return requireData(response.data, response.error);
}

export async function deleteProject(projectId: string) {
  const response = await apiClient.DELETE(
    "/api/tasks/projects/{project_id}",
    { params: { path: { project_id: projectId } } },
  );
  return requireData(
    response.data as components["schemas"]["Task"][] | undefined,
    response.error,
  );
}

export function formatProjectName(project: { id: string; name: string }): string {
  return `${project.name} (#${project.id})`;
}
