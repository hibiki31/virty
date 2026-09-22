import StorageMetadataEdit from "@/components/storages/StorageMetadataEdit.vue";
import { ButtonStub, SelectStub, componentStubs } from "@/__tests__/support/components";
import { flushPromises, mount } from "@vue/test-utils";
import { expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  patch: vi.fn(),
  trigger: vi.fn(),
  notify: vi.fn(),
}));

vi.mock("@/api", () => ({ apiClient: { PATCH: mocks.patch } }));
vi.mock("@/composables/nodes", () => ({
  getNode: vi.fn().mockResolvedValue({ count: 0, data: [] }),
  initNodeList: { count: 0, data: [] },
}));
vi.mock("@/stores/state", () => ({ useStateStore: () => ({ trigger: mocks.trigger }) }));
vi.mock("@/composables/notify", () => ({
  default: mocks.notify,
  rawTextRef: (text: string) => ({ kind: "raw", text }),
}));

it("管理者指定と選択したmetadataを送信し、成功時に閉じて一覧を更新する", async () => {
  mocks.patch.mockResolvedValue({ data: [{ uuid: "unassigned-storage" }] });
  const wrapper = mount(StorageMetadataEdit, {
    props: { modelValue: true, uuid: "unassigned-storage" },
    global: { stubs: componentStubs },
  });
  const selects = wrapper.findAllComponents(SelectStub);
  selects[0].vm.$emit("update:modelValue", "ssd");
  selects[1].vm.$emit("update:modelValue", "local");
  selects[2].vm.$emit("update:modelValue", "iso");
  await wrapper.getComponent(ButtonStub).trigger("click");
  await flushPromises();

  expect(mocks.patch).toHaveBeenCalledWith("/api/storages", {
    params: { query: { admin: true } },
    body: { uuid: "unassigned-storage", deviceType: "ssd", protocol: "local", rool: "iso" },
  });
  expect(wrapper.emitted("update:modelValue")).toEqual([[false]]);
  expect(mocks.trigger).toHaveBeenCalledOnce();
  expect(mocks.notify).toHaveBeenCalledWith(
    "success",
    { kind: "translation", key: "dialogs.storageMetadata.changed" },
    { kind: "raw", text: "unassigned-storage" },
  );
});
