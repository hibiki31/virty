import { openVNC } from "@/composables/vm";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  post: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: vi.fn(),
    PATCH: vi.fn(),
    POST: mocks.post,
  },
}));

beforeEach(() => {
  mocks.post.mockReset();
});

describe("VM console ticket", () => {
  it("one-time ticketをencodeして先に開いたwindowへ設定する", async () => {
    const consoleWindow = {
      close: vi.fn(),
      location: { href: "about:blank" },
      opener: window,
    };
    const open = vi
      .spyOn(window, "open")
      .mockReturnValue(consoleWindow as unknown as Window);
    mocks.post.mockResolvedValue({ data: { token: "ticket/a+b?" } });

    await openVNC("vm-uuid");

    expect(open).toHaveBeenCalledWith("about:blank", "_blank");
    expect(consoleWindow.opener).toBeNull();
    expect(mocks.post).toHaveBeenCalledWith(
      "/api/vms/{uuid}/console-ticket",
      { params: { path: { uuid: "vm-uuid" } } },
    );
    expect(consoleWindow.location.href).toBe(
      "/novnc/vnc.html?resize=remote&autoconnect=true" +
        "&path=novnc/websockify?token=ticket%2Fa%2Bb%3F",
    );
  });

  it("ticket取得失敗時は空windowを閉じる", async () => {
    const consoleWindow = {
      close: vi.fn(),
      location: { href: "about:blank" },
      opener: window,
    };
    vi.spyOn(window, "open").mockReturnValue(consoleWindow as unknown as Window);
    mocks.post.mockResolvedValue({
      data: undefined,
      error: {
        detail: {
          code: "scope_denied",
          message: "The required permission is missing.",
        },
      },
    });

    await openVNC("vm-uuid");

    expect(consoleWindow.close).toHaveBeenCalledOnce();
    expect(consoleWindow.location.href).toBe("about:blank");
  });
});
