import SetupDialog from "@/components/SetupDialog.vue";
import {
  ButtonStub,
  componentStubs,
  setFormValidity,
} from "@/__tests__/support/components";
import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  notify: vi.fn(),
  sleep: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: mocks.apiGet,
    POST: mocks.apiPost,
  },
}));

vi.mock("@/composables/notify", () => ({
  apiErrorRef: (error: unknown) => ({ kind: "api-error", error }),
  default: mocks.notify,
}));
vi.mock("@/composables/sleep", () => ({ asyncSleep: mocks.sleep }));

function mountDialog() {
  return mount(SetupDialog, { global: { stubs: componentStubs } });
}

function setupButton(wrapper: ReturnType<typeof mountDialog>) {
  const target = wrapper
    .findAllComponents(ButtonStub)
    .find((item) => item.text() === "Setup");
  if (!target) throw new Error("Setup buttonが見つかりません");
  return target;
}

beforeEach(() => {
  vi.clearAllMocks();
  setFormValidity(true);
  mocks.apiGet.mockResolvedValue({
    data: { initialized: true, version: "5.1.2" },
  });
  mocks.sleep.mockResolvedValue(undefined);
});

describe("SetupDialog", () => {
  it("formが無効ならAPIを呼ばずloadingを開始しない", async () => {
    setFormValidity(false);
    const wrapper = mountDialog();
    await flushPromises();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(setupButton(wrapper).props("loading")).toBe(false);
  });

  it("成功を通知して初期化状態を再取得する", async () => {
    mocks.apiPost.mockResolvedValue({
      response: new Response(null, { status: 200 }),
    });
    const wrapper = mountDialog();
    await flushPromises();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).toHaveBeenCalledOnce();
    expect(mocks.notify).toHaveBeenCalledWith("success", {
      kind: "translation",
      key: "setup.success",
    });
    expect(mocks.apiGet).toHaveBeenCalledTimes(2);
    expect(setupButton(wrapper).props("loading")).toBe(false);
  });

  it("通信失敗を通知してloadingを必ず解除する", async () => {
    mocks.apiPost.mockRejectedValue(new TypeError("network unavailable"));
    const wrapper = mountDialog();
    await flushPromises();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      { kind: "translation", key: "setup.failed" },
      { kind: "translation", key: "setup.unreachable" },
    );
    expect(setupButton(wrapper).props("loading")).toBe(false);
  });
});
