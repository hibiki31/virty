import NetworkAddDialog from "@/components/networks/NetworkAddDialog.vue";
import {
  ButtonStub,
  componentStubs,
  SelectStub,
  setFormValidity,
  TextFieldStub,
} from "@/__tests__/support/components";
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiPost: vi.fn(),
  getNode: vi.fn(),
  notify: vi.fn(),
  notifyTask: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: { POST: mocks.apiPost },
}));
vi.mock("@/composables/nodes", () => ({ getNode: mocks.getNode }));
vi.mock("@/composables/notify", () => ({
  default: mocks.notify,
  notifyTask: mocks.notifyTask,
}));

async function mountDialog(): Promise<VueWrapper> {
  const wrapper = mount(NetworkAddDialog, {
    props: { modelValue: true },
    global: { stubs: componentStubs },
  });
  await flushPromises();
  return wrapper;
}

function select(wrapper: VueWrapper, label: string) {
  const target = wrapper
    .findAllComponents(SelectStub)
    .find((item) => item.props("label") === label);
  if (!target) throw new Error(`${label} selectが見つかりません`);
  return target;
}

function field(wrapper: VueWrapper, label: string) {
  const target = wrapper
    .findAllComponents(TextFieldStub)
    .find((item) => item.props("label") === label);
  if (!target) throw new Error(`${label} fieldが見つかりません`);
  return target;
}

async function fillRequired(wrapper: VueWrapper) {
  await field(wrapper, "Name").get("input").setValue("tenant-net");
  select(wrapper, "Node").vm.$emit("update:modelValue", "node-1");
  await flushPromises();
}

beforeEach(() => {
  vi.clearAllMocks();
  setFormValidity(true);
  mocks.getNode.mockResolvedValue({
    count: 1,
    data: [{ name: "node-1" }],
  });
  mocks.apiPost.mockResolvedValue({ data: [{ uuid: "task-1" }] });
});

describe("NetworkAddDialog", () => {
  it("invalid formではrequestを送らない", async () => {
    setFormValidity(false);
    const wrapper = await mountDialog();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).not.toHaveBeenCalled();
  });

  it("NAT payloadを送りtask通知後に閉じる", async () => {
    const wrapper = await mountDialog();
    await fillRequired(wrapper);

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).toHaveBeenCalledWith("/api/tasks/networks", {
      body: expect.objectContaining({
        bridgeName: undefined,
        dhcp: { end: "192.168.0.200", start: "192.168.0.1" },
        forwardMode: "nat",
        ip: { address: "192.168.0.254", netmask: "255.255.255.0" },
        name: "tenant-net",
        nodeName: "node-1",
      }),
    });
    expect(mocks.notifyTask).toHaveBeenCalledOnce();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });

  it("bridgeとOVSでbridge名とIP設定を正しく切り替える", async () => {
    const bridgeWrapper = await mountDialog();
    await fillRequired(bridgeWrapper);
    select(bridgeWrapper, "Mode").vm.$emit("update:modelValue", "bridge");
    await field(bridgeWrapper, "Bridge Name").get("input").setValue("br-test");
    await bridgeWrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost.mock.calls[0][1].body).toMatchObject({
      bridgeName: "br-test",
      forwardMode: "bridge",
      ip: { address: "192.168.0.254" },
    });

    mocks.apiPost.mockClear();
    const ovsWrapper = await mountDialog();
    await fillRequired(ovsWrapper);
    select(ovsWrapper, "Mode").vm.$emit("update:modelValue", "ovs");
    await field(ovsWrapper, "Bridge Name").get("input").setValue("ovs-test");
    await ovsWrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost.mock.calls[0][1].body).toMatchObject({
      bridgeName: "ovs-test",
      dhcp: undefined,
      forwardMode: "ovs",
      ip: undefined,
    });
  });

  it("isolatedではbridge、IP、DHCPを送らない", async () => {
    const wrapper = await mountDialog();
    await fillRequired(wrapper);
    select(wrapper, "Mode").vm.$emit("update:modelValue", "isolated");

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost.mock.calls[0][1].body).toMatchObject({
      bridgeName: undefined,
      dhcp: undefined,
      forwardMode: "isolated",
      ip: undefined,
    });
  });

  it("API errorでは開いたまま通知しloadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({ error: { detail: "conflict" } });
    const wrapper = await mountDialog();
    await fillRequired(wrapper);

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      "Create Network failed",
      { detail: "conflict" },
    );
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    const submit = wrapper
      .findAllComponents(ButtonStub)
      .find((item) => item.attributes("data-testid") === "network-create-submit");
    expect(submit?.props("loading")).toBe(false);
  });

  it("Cancelでrequestなしに閉じる", async () => {
    const wrapper = await mountDialog();

    await wrapper.get('[data-testid="network-create-cancel"]').trigger("click");

    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });
});
