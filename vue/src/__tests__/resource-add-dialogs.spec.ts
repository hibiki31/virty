import ImageDownloadDialog from "@/components/images/ImageDownloadDialog.vue";
import NodeAddDialog from "@/components/nodes/NodeAddDialog.vue";
import StorageAddDialog from "@/components/storages/StorageAddDialog.vue";
import {
  ButtonStub,
  componentStubs,
  setFormValidity,
} from "@/__tests__/support/components";
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import type { Component } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiPost: vi.fn(),
  getNode: vi.fn(),
  getStorageList: vi.fn(),
  notify: vi.fn(),
  notifyTask: vi.fn(),
  useNotificationNotify: vi.fn(),
}));

vi.mock("@/api", () => ({ apiClient: { POST: mocks.apiPost } }));
vi.mock("@/composables/nodes", () => ({
  getNode: mocks.getNode,
  initNodeList: { count: 0, data: [] },
}));
vi.mock("@/composables/storage", () => ({
  getStorageList: mocks.getStorageList,
  initStorageList: { count: 0, data: [] },
}));
vi.mock("@/composables/notify", () => ({
  default: mocks.notify,
  notifyTask: mocks.notifyTask,
}));
vi.mock("@kyvg/vue3-notification", () => ({
  useNotification: () => ({ notify: mocks.useNotificationNotify }),
}));

function button(wrapper: VueWrapper, text: string) {
  const target = wrapper
    .findAllComponents(ButtonStub)
    .find((item) => item.text() === text);
  if (!target) throw new Error(`${text} buttonが見つかりません`);
  return target;
}

async function mountDialog(component: Component): Promise<VueWrapper> {
  const wrapper = mount(component, {
    props: { modelValue: true },
    global: { stubs: componentStubs },
  });
  await flushPromises();
  return wrapper;
}

beforeEach(() => {
  vi.clearAllMocks();
  setFormValidity(true);
  mocks.getNode.mockResolvedValue({ count: 1, data: [{ name: "node-1" }] });
  mocks.getStorageList.mockResolvedValue({ count: 0, data: [] });
});

describe("NodeAddDialog", () => {
  it("invalid formではrequestを送らない", async () => {
    setFormValidity(false);
    const wrapper = await mountDialog(NodeAddDialog);
    button(wrapper, "Register").element.click();
    await flushPromises();
    expect(mocks.apiPost).not.toHaveBeenCalled();
  });

  it("成功時に通知して閉じ、loadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({
      response: new Response(null, { status: 200 }),
    });
    const wrapper = await mountDialog(NodeAddDialog);
    button(wrapper, "Register").element.click();
    await flushPromises();

    expect(mocks.apiPost).toHaveBeenCalledWith("/api/tasks/nodes", {
      body: expect.objectContaining({ port: 22 }),
    });
    expect(mocks.useNotificationNotify).toHaveBeenCalledWith(
      expect.objectContaining({ type: "success" }),
    );
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
    expect(button(wrapper, "Register").props("loading")).toBe(false);
  });

  it("API failureを通知して開いたままloadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({
      error: { detail: "invalid node" },
      response: new Response(null, { status: 422 }),
    });
    const wrapper = await mountDialog(NodeAddDialog);
    button(wrapper, "Register").element.click();
    await flushPromises();

    expect(mocks.useNotificationNotify).toHaveBeenCalledWith(
      expect.objectContaining({ type: "error" }),
    );
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(button(wrapper, "Register").props("loading")).toBe(false);
  });

  it("Cancelでrequestなしに閉じる", async () => {
    const wrapper = await mountDialog(NodeAddDialog);
    await button(wrapper, "Cancel").trigger("click");
    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });
});

describe("StorageAddDialog", () => {
  it("invalid formではrequestを送らない", async () => {
    setFormValidity(false);
    const wrapper = await mountDialog(StorageAddDialog);
    await wrapper.get("form").trigger("submit");
    await flushPromises();
    expect(mocks.apiPost).not.toHaveBeenCalled();
  });

  it("成功時にtaskを通知して閉じ、loadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({ data: [{ uuid: "storage-task" }] });
    const wrapper = await mountDialog(StorageAddDialog);
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notifyTask).toHaveBeenCalledWith("storage-task");
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
    expect(button(wrapper, "ADD").props("loading")).toBe(false);
  });

  it("API failureを通知して開いたままloadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({ error: { detail: "storage conflict" } });
    const wrapper = await mountDialog(StorageAddDialog);
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      "Register Storage failed",
      { detail: "storage conflict" },
    );
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(button(wrapper, "ADD").props("loading")).toBe(false);
  });

  it("Cancelでrequestなしに閉じる", async () => {
    const wrapper = await mountDialog(StorageAddDialog);
    await button(wrapper, "Cancel").trigger("click");
    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });
});

describe("ImageDownloadDialog", () => {
  it("invalid formではrequestを送らない", async () => {
    setFormValidity(false);
    const wrapper = await mountDialog(ImageDownloadDialog);
    await wrapper.get("form").trigger("submit");
    await flushPromises();
    expect(mocks.apiPost).not.toHaveBeenCalled();
  });

  it("成功時にtaskを通知して閉じ、loadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({ data: [{ uuid: "image-task" }] });
    const wrapper = await mountDialog(ImageDownloadDialog);
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notifyTask).toHaveBeenCalledWith("image-task");
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
    expect(button(wrapper, "ADD").props("loading")).toBe(false);
  });

  it("API failureを通知して開いたままloadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({ error: { detail: "download failed" } });
    const wrapper = await mountDialog(ImageDownloadDialog);
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      "Download Image failed",
      { detail: "download failed" },
    );
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(button(wrapper, "ADD").props("loading")).toBe(false);
  });

  it("Cancelでrequestなしに閉じる", async () => {
    const wrapper = await mountDialog(ImageDownloadDialog);
    await button(wrapper, "Cancel").trigger("click");
    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });
});
