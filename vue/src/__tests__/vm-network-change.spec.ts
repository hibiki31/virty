import VMNetworkChange from "@/components/vms/VMNetworkChange.vue";
import type { schemas } from "@/composables/schemas";
import { componentStubs } from "@/__tests__/support/components";
import { flushPromises, shallowMount } from "@vue/test-utils";
import { defineComponent, nextTick, type PropType } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: mocks.apiGet,
    PATCH: mocks.apiPatch,
  },
}));

const SelectStub = defineComponent({
  name: "VSelect",
  props: {
    items: { type: Array as PropType<unknown[]>, default: () => [] },
    label: String,
    modelValue: String,
  },
  emits: ["update:modelValue"],
  template: '<div :data-label="label"></div>',
});

const vm = {
  uuid: "vm-1",
  name: "vm-1",
  nodeName: "node-1",
  ownerProjectId: "a1b2c3",
} as unknown as schemas["DomainDetail"];

beforeEach(() => {
  vi.clearAllMocks();
  mocks.apiGet.mockResolvedValue({
    data: {
      count: 1,
      data: [{
        uuid: "network-1",
        name: "ovs-1",
        nodeName: "node-1",
        type: "openvswitch",
        portgroups: [{ name: "tenant-a", vlanId: "321", isDefault: false }],
      }],
    },
  });
});

describe("VMNetworkChange Project network boundary", () => {
  it("閉じた状態でmountしてもdialogを開いた時に候補を取得する", async () => {
    const wrapper = shallowMount(VMNetworkChange, {
      props: { modelValue: false, item: vm, mac: "52:54:00:00:00:01" },
      global: { stubs: { ...componentStubs, VSelect: SelectStub } },
    });

    expect(mocks.apiGet).not.toHaveBeenCalled();
    await wrapper.setProps({ modelValue: true });
    await flushPromises();

    expect(mocks.apiGet).toHaveBeenCalledWith("/api/networks", {
      params: {
        query: {
          admin: false,
          nodeNameLike: "node-1",
          projectId: "a1b2c3",
        },
      },
    });
  });

  it("VM所有Projectでnetworkを絞り、応答内のportgroup名だけを候補にする", async () => {
    const wrapper = shallowMount(VMNetworkChange, {
      props: { modelValue: true, item: vm, mac: "52:54:00:00:00:01" },
      global: { stubs: { ...componentStubs, VSelect: SelectStub } },
    });
    await flushPromises();

    expect(mocks.apiGet).toHaveBeenCalledWith("/api/networks", {
      params: {
        query: {
          admin: false,
          nodeNameLike: "node-1",
          projectId: "a1b2c3",
        },
      },
    });

    const networkSelect = wrapper.findAllComponents(SelectStub)
      .find(select => select.props("label") === "Network");
    expect(networkSelect).toBeDefined();
    networkSelect!.vm.$emit("update:modelValue", "network-1");
    await nextTick();

    const portSelect = wrapper.findAllComponents(SelectStub)
      .find(select => select.props("label") === "Port");
    expect(portSelect?.props("items")).toEqual([
      { title: "tenant-a (321)", value: "tenant-a" },
    ]);
  });
});
