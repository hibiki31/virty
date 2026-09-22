import { openVNC } from "@/composables/vm";
import { translationRef } from "@/composables/i18n";
import { apiErrorRef } from "@/composables/notify";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  post: vi.fn(),
  notify: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: vi.fn(),
    PATCH: vi.fn(),
    POST: mocks.post,
  },
}));

vi.mock("@/composables/notify", () => ({
  default: mocks.notify,
  apiErrorRef: (error: unknown) => ({ kind: "api-error", error }),
}));

beforeEach(() => {
  mocks.post.mockReset();
  mocks.notify.mockReset();
  vi.restoreAllMocks();
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

  it("ticket取得失敗時は空windowを閉じてAPIの失敗理由を通知する", async () => {
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
    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      translationRef("pages.vmDetail.notifications.consoleFailed"),
      apiErrorRef({
        detail: {
          code: "scope_denied",
          message: "The required permission is missing.",
        },
      }),
    );
  });

  it("通信例外でも空windowを閉じて失敗を通知する", async () => {
    const consoleWindow = {
      close: vi.fn(),
      location: { href: "about:blank" },
      opener: window,
    };
    vi.spyOn(window, "open").mockReturnValue(consoleWindow as unknown as Window);
    mocks.post.mockRejectedValue(new Error("network failure"));

    await openVNC("vm-uuid");

    expect(consoleWindow.close).toHaveBeenCalledOnce();
    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      translationRef("pages.vmDetail.notifications.consoleFailed"),
      translationRef("pages.vmDetail.notifications.consoleUnreachable"),
    );
  });
});
