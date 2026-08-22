import {
  getNetworkList,
  initNetworkList,
} from "@/composables/network";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { get } = vi.hoisted(() => ({
  get: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: get,
  },
}));

describe("network一覧API", () => {
  beforeEach(() => {
    get.mockReset();
  });

  it("UIの1ページ目をAPIの0ページ目へ変換してresponseを返す", async () => {
    const response = { count: 2, data: [] };
    const query = { admin: true, limit: 20, page: 1 };
    get.mockResolvedValue({ data: response });

    await expect(getNetworkList(query)).resolves.toBe(response);

    expect(get).toHaveBeenCalledOnce();
    expect(get).toHaveBeenCalledWith("/api/networks", {
      params: {
        query: { admin: true, limit: 20, page: 0 },
      },
    });
    expect(query.page).toBe(1);
  });

  it("response dataがない場合は空の一覧へfallbackする", async () => {
    get.mockResolvedValue({ error: { detail: "unavailable" } });

    await expect(
      getNetworkList({ admin: true, limit: 20, page: 1 })
    ).resolves.toBe(initNetworkList);
  });
});
