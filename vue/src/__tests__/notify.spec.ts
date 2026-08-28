import notify, {
  formatNotificationText,
  notifyTask,
} from "@/composables/notify";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  baseNotify: vi.fn(),
}));

vi.mock("@kyvg/vue3-notification", () => ({
  useNotification: () => ({ notify: mocks.baseNotify }),
}));

describe("API notification", () => {
  beforeEach(() => {
    mocks.baseNotify.mockReset();
  });

  it("stringと空値を利用者向けmessageへ変換する", () => {
    expect(formatNotificationText("failed")).toBe("failed");
    expect(formatNotificationText("")).toBe("Unknown error");
    expect(formatNotificationText(undefined)).toBe("Unknown error");
  });

  it("422 validation detailを欠落させず連結する", () => {
    const error = {
      detail: [
        { loc: ["body", "name"], msg: "Name is required", type: "missing" },
        { loc: ["body", "port"], msg: "Port is invalid", type: "value_error" },
      ],
    };

    expect(formatNotificationText(error)).toBe(
      "Name is required; Port is invalid",
    );

    notify("error", "Request failed", error);
    expect(mocks.baseNotify).toHaveBeenCalledWith({
      type: "error",
      title: "Request failed",
      text: "Name is required; Port is invalid",
    });

    expect(formatNotificationText({
      detail: [{ loc: ["body"], msg: "", type: "missing" }],
    })).toBe("Unknown error");
  });

  it("文字列detailと構造不明のdetailを安全に整形する", () => {
    expect(formatNotificationText({ detail: "Conflict" })).toBe("Conflict");
    expect(formatNotificationText({ detail: "" })).toBe("Unknown error");
    expect(formatNotificationText({})).toBe("Unknown error");

    notify("success");
    expect(mocks.baseNotify).toHaveBeenCalledWith({
      type: "success",
      title: "Success",
      text: "API request completed",
    });
  });

  it("409の構造化detailへresource一覧を含める", () => {
    expect(formatNotificationText({
      detail: {
        message: "VM resources are outside the destination project grants",
        resources: ["storage:/vm/disk.qcow2", "network:tenant"],
      },
    })).toBe(
      "VM resources are outside the destination project grants: "
      + "storage:/vm/disk.qcow2, network:tenant",
    );

    expect(formatNotificationText({
      detail: {
        message: "Project is in use",
        resources: [42, null],
      },
    })).toBe("Project is in use");
    expect(formatNotificationText({
      detail: { message: "   ", resources: ["vm:one"] },
    })).toBe("Unknown error");
  });

  it("task UUIDをqueue通知へ含め、欠落時は空文字にする", () => {
    notifyTask("task-1");
    notifyTask(undefined);

    expect(mocks.baseNotify).toHaveBeenNthCalledWith(1, {
      type: "success",
      title: "Task has been queued",
      text: "task-1",
    });
    expect(mocks.baseNotify).toHaveBeenNthCalledWith(2, {
      type: "success",
      title: "Task has been queued",
      text: "",
    });
  });
});
