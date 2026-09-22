import VMCdromChange from "@/components/vms/VMCdromChange.vue";
import type { schemas } from "@/composables/schemas";
import { componentStubs } from "@/__tests__/support/components";
import { flushPromises, shallowMount } from "@vue/test-utils";
import { defineComponent, type PropType } from "vue";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  patch: vi.fn(),
  scopes: [] as string[],
}));

vi.mock("@/api", () => ({ apiClient: { GET: mocks.get, PATCH: mocks.patch } }));
vi.mock("@/stores/auth", () => ({ useAuthStore: () => ({ scopes: mocks.scopes }) }));

const SelectStub = defineComponent({
  name: "VSelect",
  props: {
    items: { type: Array as PropType<string[]>, default: () => [] },
    modelValue: String,
  },
  template: "<div />",
});

const vm = {
  uuid: "vm-1",
  nodeName: "node-1",
  ownerProjectId: "project-1",
} as schemas["DomainDetail"];

beforeEach(() => {
  vi.clearAllMocks();
  mocks.scopes = [];
  mocks.get.mockResolvedValue({
    data: { count: 1, data: [{ path: "/iso/install.iso" }] },
  });
});

it("ダイアログを開いた時にVMのノードと所属ProjectでISO候補を取得する", async () => {
  const wrapper = shallowMount(VMCdromChange, {
    props: { modelValue: false, item: vm, target: "sda" },
    global: { stubs: { ...componentStubs, VSelect: SelectStub } },
  });

  expect(mocks.get).not.toHaveBeenCalled();
  await wrapper.setProps({ modelValue: true });
  await flushPromises();

  expect(mocks.get).toHaveBeenCalledWith("/api/images", {
    params: {
      query: { admin: false, limit: 0, nameLike: ".iso", nodeName: "node-1", projectId: "project-1" },
    },
  });
  expect(wrapper.getComponent(SelectStub).props("items")).toEqual(["/iso/install.iso"]);
});

it("管理者はProject grantに依存しない一覧を取得し、マウントにも管理者指定を付ける", async () => {
  mocks.scopes = ["admin"];
  mocks.patch.mockResolvedValue({ data: [{ uuid: "task-1" }] });
  const wrapper = shallowMount(VMCdromChange, {
    props: { modelValue: true, item: vm, target: "sda" },
    global: { stubs: { ...componentStubs, VSelect: SelectStub } },
  });
  await flushPromises();

  expect(mocks.get).toHaveBeenCalledWith("/api/images", {
    params: {
      query: { admin: true, limit: 0, nameLike: ".iso", nodeName: "node-1", projectId: undefined },
    },
  });

  wrapper.getComponent(SelectStub).vm.$emit("update:modelValue", "/iso/install.iso");
  await wrapper.find("form").trigger("submit");
  await flushPromises();

  expect(mocks.patch).toHaveBeenCalledWith("/api/tasks/vms/{uuid}/cdrom", {
    params: { path: { uuid: "vm-1" }, query: { admin: true } },
    body: { target: "sda", path: "/iso/install.iso" },
  });
});
