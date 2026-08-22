import { getImageList } from "@/composables/image";
import { getNetworkList } from "@/composables/network";
import { toApiPageQuery } from "@/composables/pagination";
import { getStorageList } from "@/composables/storage";
import { getTaskList } from "@/composables/task";
import { getUserList } from "@/composables/user";
import { getVMList } from "@/composables/vm";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: mocks.get,
  },
}));

type CommonQuery = {
  admin: boolean;
  limit: number;
  page: number;
};

const cases: Array<{
  endpoint: string;
  load: (query: CommonQuery) => Promise<unknown>;
  name: string;
}> = [
  { endpoint: "/api/vms", load: getVMList, name: "VM" },
  { endpoint: "/api/networks", load: getNetworkList, name: "network" },
  { endpoint: "/api/storages", load: getStorageList, name: "storage" },
  { endpoint: "/api/images", load: getImageList, name: "image" },
  { endpoint: "/api/tasks", load: getTaskList, name: "task" },
  { endpoint: "/api/users", load: getUserList, name: "user" },
];

describe("page query変換", () => {
  it("未指定とnullを先頭pageとして扱い、0を負数にしない", () => {
    expect(toApiPageQuery({ limit: 20, page: undefined })).toEqual({
      limit: 20,
      page: 0,
    });
    expect(toApiPageQuery({ limit: 20, page: null })).toEqual({
      limit: 20,
      page: 0,
    });
    expect(toApiPageQuery({ limit: 20, page: 0 })).toEqual({
      limit: 20,
      page: 0,
    });
  });
});

describe.each(cases)("$name一覧のpagination", ({ endpoint, load }) => {
  beforeEach(() => {
    mocks.get.mockReset();
    mocks.get.mockResolvedValue({ data: { count: 0, data: [] } });
  });

  it("同じqueryを連続利用してもUI pageとAPI pageがずれない", async () => {
    const query = { admin: true, limit: 20, page: 3 };

    await load(query);
    await load(query);

    expect(query).toEqual({ admin: true, limit: 20, page: 3 });
    expect(mocks.get).toHaveBeenCalledTimes(2);
    expect(mocks.get).toHaveBeenNthCalledWith(1, endpoint, {
      params: { query: { admin: true, limit: 20, page: 2 } },
    });
    expect(mocks.get).toHaveBeenNthCalledWith(2, endpoint, {
      params: { query: { admin: true, limit: 20, page: 2 } },
    });
  });
});
