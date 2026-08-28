import {
  addProjectMember,
  formatProjectName,
  getProjectList,
  getProjectResourceGrantCandidates,
  removeProjectMember,
  replaceProjectResourceGrants,
  updateProjectName,
} from "@/composables/project";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiDelete: vi.fn(),
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPut: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    DELETE: mocks.apiDelete,
    GET: mocks.apiGet,
    PATCH: mocks.apiPatch,
    PUT: mocks.apiPut,
  },
}));

const detail = {
  id: "a1b2c3",
  name: "Project A",
  memberCount: 1,
  usedCore: 0,
  usedMemoryG: 0,
  usedStorageG: 0,
  limits: { core: 0, memoryG: 0, storageCapacityG: 0, enforced: false },
  members: [{ username: "alice" }],
  resourceGrants: { storagePoolIds: [], networkPoolIds: [], flavorIds: [] },
  storagePools: [],
  networkPools: [],
  flavors: [],
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.apiGet.mockResolvedValue({ data: { count: 1, data: [detail] } });
  mocks.apiPatch.mockResolvedValue({ data: detail });
  mocks.apiPut.mockResolvedValue({ data: detail });
  mocks.apiDelete.mockResolvedValue({ data: detail });
});

describe("Project API", () => {
  it("一覧queryのpageをAPIの0始まりへ変換する", async () => {
    await getProjectList({ limit: 20, page: 2, nameLike: "A" });

    expect(mocks.apiGet).toHaveBeenCalledWith("/api/projects", {
      params: {
        query: { limit: 20, page: 1, nameLike: "A" },
      },
    });
  });

  it("名称・member・grantをそれぞれ専用endpointへ送る", async () => {
    await updateProjectName("a1b2c3", { name: "Renamed" });
    await addProjectMember("a1b2c3", "bob");
    await removeProjectMember("a1b2c3", "bob");
    await replaceProjectResourceGrants("a1b2c3", {
      storagePoolIds: [1],
      networkPoolIds: [2],
      flavorIds: [3],
    });

    expect(mocks.apiPatch).toHaveBeenCalledWith(
      "/api/projects/{project_id}",
      { params: { path: { project_id: "a1b2c3" } }, body: { name: "Renamed" } },
    );
    expect(mocks.apiPut).toHaveBeenCalledWith(
      "/api/projects/{project_id}/members/{username}",
      { params: { path: { project_id: "a1b2c3", username: "bob" } } },
    );
    expect(mocks.apiDelete).toHaveBeenCalledWith(
      "/api/projects/{project_id}/members/{username}",
      { params: { path: { project_id: "a1b2c3", username: "bob" } } },
    );
    expect(mocks.apiPut).toHaveBeenCalledWith(
      "/api/projects/{project_id}/resource-grants",
      {
        params: { path: { project_id: "a1b2c3" } },
        body: { storagePoolIds: [1], networkPoolIds: [2], flavorIds: [3] },
      },
    );
  });

  it("grant候補を通常resource一覧ではなくProject専用endpointから取得する", async () => {
    mocks.apiGet.mockResolvedValueOnce({
      data: { storagePools: [], networkPools: [], flavors: [] },
    });

    await getProjectResourceGrantCandidates("a1b2c3");

    expect(mocks.apiGet).toHaveBeenCalledWith(
      "/api/projects/{project_id}/resource-grant-candidates",
      { params: { path: { project_id: "a1b2c3" } } },
    );
  });

  it("同名ProjectをID付きで識別できる表記にする", () => {
    expect(formatProjectName({ id: "a1b2c3", name: "Shared" })).toBe(
      "Shared (#a1b2c3)",
    );
  });
});
