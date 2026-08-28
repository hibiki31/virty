import VMAddDialog from "@/components/vms/VMAddDialog.vue";
import { setLocale } from "@/plugins/i18n";
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import {
  defineComponent,
  h,
  nextTick,
  type Component,
  type PropType,
} from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  auth: { username: "alice" },
  getImageList: vi.fn(),
  getNetworkList: vi.fn(),
  getNode: vi.fn(),
  getProjectList: vi.fn(),
  getStorageList: vi.fn(),
  notify: vi.fn(),
  notifyTask: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: mocks.apiGet,
    POST: mocks.apiPost,
  },
}));

vi.mock("@/composables/nodes", () => ({
  initNodeList: { count: 0, data: [] },
  getNode: mocks.getNode,
}));

vi.mock("@/composables/network", () => ({
  initNetworkList: { count: 0, data: [] },
  getNetworkList: mocks.getNetworkList,
}));

vi.mock("@/composables/storage", () => ({
  initStorageList: { count: 0, data: [] },
  getStorageList: mocks.getStorageList,
}));

vi.mock("@/composables/image", () => ({
  initImageList: { count: 0, data: [] },
  getImageList: mocks.getImageList,
}));

vi.mock("@/composables/project", () => ({
  formatProjectName: (project: { id: string; name: string }) =>
    `${project.name} (#${project.id})`,
  getProjectList: mocks.getProjectList,
}));

vi.mock("@/composables/notify", () => ({
  apiErrorRef: (error: unknown) => ({ kind: "api-error", error }),
  default: mocks.notify,
  notifyTask: mocks.notifyTask,
}));

vi.mock("@/stores/auth", () => ({
  useAuthStore: () => mocks.auth,
}));

const ContainerStub = defineComponent({
  inheritAttrs: false,
  template: '<div v-bind="$attrs"><slot /></div>',
});

const ButtonStub = defineComponent({
  name: "VBtn",
  inheritAttrs: false,
  props: { loading: Boolean, type: String },
  emits: ["click"],
  template:
    '<button v-bind="$attrs" :type="type || \'button\'" @click="$emit(\'click\')"><slot /></button>',
});

let formValid = true;

const FormStub = defineComponent({
  name: "VForm",
  emits: ["submit"],
  setup(_, { emit, slots }) {
    return () =>
      h(
        "form",
        {
          onSubmit(event: Event) {
            event.preventDefault();
            const submitEvent = Object.assign(
              Promise.resolve({ valid: formValid }),
              { preventDefault() {} }
            );
            emit("submit", submitEvent);
          },
        },
        slots.default?.()
      );
  },
});

const TextFieldStub = defineComponent({
  name: "VTextField",
  inheritAttrs: false,
  props: {
    label: String,
    modelValue: { type: [String, Number] as PropType<string | number> },
    type: String,
  },
  emits: ["change", "update:modelValue"],
  template: `
    <label v-bind="$attrs">
      {{ label }}
      <input
        :type="type || 'text'"
        :value="modelValue ?? ''"
        @input="$emit('update:modelValue', $event.target.value)"
        @change="$emit('change', $event.target.value)"
      >
    </label>
  `,
});

const TextareaStub = defineComponent({
  name: "VTextarea",
  inheritAttrs: false,
  props: {
    errorMessages: { type: [String, Array] as PropType<string | string[]> },
    label: String,
    modelValue: String,
  },
  emits: ["update:modelValue"],
  template: `
    <label v-bind="$attrs">
      {{ label }}
      <textarea
        :value="modelValue ?? ''"
        @input="$emit('update:modelValue', $event.target.value)"
      ></textarea>
      <span class="error-messages">{{ errorMessages }}</span>
    </label>
  `,
});

const CheckboxStub = defineComponent({
  name: "VCheckbox",
  inheritAttrs: false,
  props: {
    label: String,
    modelValue: Boolean,
  },
  emits: ["update:modelValue"],
  template: `
    <label v-bind="$attrs">
      <input
        type="checkbox"
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
      >
      {{ label }}
    </label>
  `,
});

const SelectStub = defineComponent({
  name: "VSelect",
  inheritAttrs: false,
  props: {
    items: { type: Array as PropType<unknown[]>, default: () => [] },
    label: String,
    loading: Boolean,
    modelValue: { type: null },
  },
  emits: ["update:modelValue"],
  template: '<div v-bind="$attrs">{{ label }}</div>',
});

const TabsStub = defineComponent({
  name: "VTabs",
  inheritAttrs: false,
  props: { modelValue: String },
  template: '<div v-bind="$attrs"><slot /></div>',
});

const TabStub = defineComponent({
  name: "VTab",
  props: { value: String },
  emits: ["click"],
  template: '<button type="button" @click="$emit(\'click\')"><slot /></button>',
});

const componentStubs: Record<string, Component> = {
  VAlert: ContainerStub,
  VBtn: ButtonStub,
  VCard: ContainerStub,
  VCardActions: ContainerStub,
  VCardText: ContainerStub,
  VCardTitle: ContainerStub,
  VCheckbox: CheckboxStub,
  VCol: ContainerStub,
  VDialog: ContainerStub,
  VDivider: ContainerStub,
  VForm: FormStub,
  VRow: ContainerStub,
  VSelect: SelectStub,
  VTab: TabStub,
  VTabs: TabsStub,
  VTextField: TextFieldStub,
  VTextarea: TextareaStub,
  VWindow: ContainerStub,
  VWindowItem: ContainerStub,
};

async function mountDialog(): Promise<VueWrapper> {
  const wrapper = mount(VMAddDialog, {
    props: { modelValue: true },
    global: { stubs: componentStubs },
  });
  await flushPromises();
  return wrapper;
}

async function toggleCloudInit(wrapper: VueWrapper, enabled: boolean) {
  await wrapper
    .get('[data-testid="cloud-init-toggle"] input')
    .setValue(enabled);
  await flushPromises();
}

function getTextareaStub(wrapper: VueWrapper, testId: string) {
  const component = wrapper
    .findAllComponents(TextareaStub)
    .find(item => item.attributes("data-testid") === testId);
  if (!component) {
    throw new Error(`${testId} textarea stub was not found.`);
  }
  return component;
}

function getSelectStub(wrapper: VueWrapper, testId: string) {
  const component = wrapper
    .findAllComponents(SelectStub)
    .find(item => item.attributes("data-testid") === testId);
  if (!component) {
    throw new Error(`${testId} select stub was not found.`);
  }
  return component;
}

function getCheckboxStub(wrapper: VueWrapper, testId: string) {
  const component = wrapper
    .findAllComponents(CheckboxStub)
    .find(item => item.attributes("data-testid") === testId);
  if (!component) {
    throw new Error(`${testId} checkbox stub was not found.`);
  }
  return component;
}

beforeEach(() => {
  vi.clearAllMocks();
  formValid = true;
  mocks.auth.username = "alice";
  mocks.getNode.mockResolvedValue({ count: 0, data: [] });
  mocks.getNetworkList.mockResolvedValue({ count: 0, data: [] });
  mocks.getStorageList.mockResolvedValue({ count: 0, data: [] });
  mocks.getImageList.mockResolvedValue({ count: 0, data: [] });
  mocks.getProjectList.mockResolvedValue({
    count: 1,
    data: [{
      id: "a1b2c3",
      name: "Project A",
      memberCount: 1,
      usedCore: 0,
      usedMemoryG: 0,
      usedStorageG: 0,
    }],
  });
  mocks.apiGet.mockResolvedValue({ data: { count: 0, data: [] } });
  mocks.apiPost.mockResolvedValue({ data: [{ uuid: "task-1" }] });
});

describe("VMAddDialog submit", () => {
  it("invalid formではrequestを送らない", async () => {
    formValid = false;
    const wrapper = await mountDialog();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).not.toHaveBeenCalled();
  });

  it("基本VM payloadを1回送りtask通知後に閉じる", async () => {
    mocks.getNode.mockResolvedValue({ count: 1, data: [{ name: "node-1" }] });
    mocks.getStorageList.mockResolvedValue({
      count: 1,
      data: [{ name: "pool-1", nodeName: "node-1", uuid: "pool-1" }],
    });
    mocks.getNetworkList.mockResolvedValue({
      count: 1,
      data: [{ name: "net-1", nodeName: "node-1", type: "bridge", uuid: "net-1" }],
    });
    const wrapper = await mountDialog();

    await wrapper.get('[data-testid="vm-name"] input').setValue("vm-1");
    getSelectStub(wrapper, "vm-node").vm.$emit("update:modelValue", "node-1");
    wrapper
      .findAllComponents(SelectStub)
      .find((item) => item.props("label") === "Destination pool")!
      .vm.$emit("update:modelValue", "pool-1");
    wrapper
      .findAllComponents(SelectStub)
      .find((item) => item.props("label") === "Network")!
      .vm.$emit("update:modelValue", "net-1");
    await flushPromises();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).toHaveBeenCalledOnce();
    expect(mocks.apiPost.mock.calls[0][1].body).toMatchObject({
      cloudInit: null,
      name: "vm-1",
      nodeName: "node-1",
      projectId: "a1b2c3",
      disks: [{ savePoolUuid: "pool-1", type: "empty" }],
      interface: [{ networkUuid: "net-1", type: "network" }],
    });
    expect(mocks.notifyTask).toHaveBeenCalledOnce();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });

  it("選択Projectを全resource queryと作成payloadへ固定する", async () => {
    mocks.getProjectList.mockResolvedValue({
      count: 2,
      data: [
        { id: "a1b2c3", name: "Project A" },
        { id: "d4e5f6", name: "Project B" },
      ],
    });
    const wrapper = await mountDialog();

    getSelectStub(wrapper, "vm-project").vm.$emit("update:modelValue", "d4e5f6");
    await flushPromises();

    expect(mocks.getNode).toHaveBeenCalledWith("d4e5f6");
    expect(mocks.getNetworkList).toHaveBeenCalledWith(expect.objectContaining({ projectId: "d4e5f6" }));
    expect(mocks.getStorageList).toHaveBeenCalledWith(expect.objectContaining({ projectId: "d4e5f6" }));
    expect(mocks.getImageList).toHaveBeenCalledWith(expect.objectContaining({ projectId: "d4e5f6" }));
  });

  it("OVS portgroup名を表示値とVM作成payloadへ使用する", async () => {
    mocks.getNode.mockResolvedValue({ count: 1, data: [{ name: "node-1" }] });
    mocks.getNetworkList.mockResolvedValue({
      count: 1,
      data: [{
        name: "ovs-1",
        nodeName: "node-1",
        type: "openvswitch",
        uuid: "network-1",
        portgroups: [{ name: "tenant-a", vlanId: "321", isDefault: false }],
      }],
    });
    const wrapper = await mountDialog();

    getSelectStub(wrapper, "vm-node").vm.$emit("update:modelValue", "node-1");
    getSelectStub(wrapper, "vm-network").vm.$emit("update:modelValue", "network-1");
    await nextTick();

    const portSelect = getSelectStub(wrapper, "vm-network-port");
    expect(portSelect.props("items")).toEqual([
      { title: "tenant-a", value: "tenant-a" },
    ]);
    portSelect.vm.$emit("update:modelValue", "tenant-a");
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost.mock.calls[0][1].body.interface).toEqual([
      expect.objectContaining({
        networkUuid: "network-1",
        port: "tenant-a",
      }),
    ]);
  });

  it("API errorを通知して開いたままloadingを解除する", async () => {
    mocks.apiPost.mockResolvedValue({
      error: {
        detail: {
          code: "conflict",
          message: "The request conflicts with the current state.",
        },
      },
    });
    const wrapper = await mountDialog();

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.notify).toHaveBeenCalledWith(
      "error",
      { kind: "translation", key: "dialogs.vmAdd.failed" },
      {
        kind: "api-error",
        error: {
          detail: {
            code: "conflict",
            message: "The request conflicts with the current state.",
          },
        },
      },
    );
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(wrapper.getComponent(ButtonStub).props("loading")).toBe(false);
  });

  it("Cancelでrequestなしに閉じる", async () => {
    const wrapper = await mountDialog();

    await wrapper.get('[data-testid="vm-create-cancel"]').trigger("click");

    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(wrapper.emitted("update:modelValue")?.slice(-1)[0]).toEqual([false]);
  });
});

describe("VMAddDialog cloud-init support", () => {
  it("simple formの変更を警告し、Apply後にYAML tabへ切り替える", async () => {
    const wrapper = await mountDialog();
    await toggleCloudInit(wrapper, true);

    expect(wrapper.find('[data-testid="cloud-init-package-update"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="cloud-init-packages"]').exists()).toBe(false);

    expect(wrapper.getComponent(TabsStub).props("modelValue")).toBe("simple");
    const tabs = wrapper.findAllComponents(TabStub);
    await tabs.find(tab => tab.text() === "YAML")!.trigger("click");
    expect(wrapper.getComponent(TabsStub).props("modelValue")).toBe("yaml");
    await tabs.find(tab => tab.text() === "Simple form")!.trigger("click");

    await wrapper
      .get('[data-testid="cloud-init-username"] input')
      .setValue("operator");
    expect(wrapper.find('[data-testid="cloud-init-dirty-warning"]').exists()).toBe(true);

    await wrapper.get('[data-testid="cloud-init-apply"]').trigger("click");
    await nextTick();

    expect(wrapper.getComponent(TabsStub).props("modelValue")).toBe("yaml");
    expect(
      wrapper.get('[data-testid="cloud-init-yaml"] textarea').element
    ).toHaveProperty("value", expect.stringContaining("operator"));
    expect(wrapper.find('[data-testid="cloud-init-dirty-warning"]').exists()).toBe(false);
  });

  it("未適用の無効なhelper入力があっても現在のraw YAMLを送信する", async () => {
    const wrapper = await mountDialog();
    await toggleCloudInit(wrapper, true);

    await wrapper
      .get('[data-testid="cloud-init-ssh-password-authentication"] input')
      .setValue(true);
    const rawYaml = "#cloud-config\npackage_update: true\n";
    await wrapper
      .get('[data-testid="cloud-init-yaml"] textarea')
      .setValue(rawYaml);

    expect(wrapper.find('[data-testid="cloud-init-dirty-warning"]').exists()).toBe(true);
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).toHaveBeenCalledOnce();
    expect(mocks.apiPost.mock.calls[0][1].body.cloudInit.userData).toBe(rawYaml);
  });

  it("不正なraw YAMLではsubmitせずYAML tabにerrorを表示する", async () => {
    const wrapper = await mountDialog();
    await toggleCloudInit(wrapper, true);

    await wrapper
      .get('[data-testid="cloud-init-yaml"] textarea')
      .setValue("#cloud-config\nusers: [");
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(wrapper.getComponent(TabsStub).props("modelValue")).toBe("yaml");
    expect(getTextareaStub(wrapper, "cloud-init-yaml").props("errorMessages")).toContain(
      "The YAML is invalid.",
    );

    setLocale("ja");
    await nextTick();
    expect(getTextareaStub(wrapper, "cloud-init-yaml").props("errorMessages")).toContain(
      "YAMLの形式が正しくありません。",
    );
  });

  it("YAML clear操作のnullを空文字へ正規化し、検証errorとして扱う", async () => {
    const wrapper = await mountDialog();
    await toggleCloudInit(wrapper, true);

    getTextareaStub(wrapper, "cloud-init-yaml").vm.$emit(
      "update:modelValue",
      null,
    );
    await nextTick();
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).not.toHaveBeenCalled();
    expect(
      wrapper.get('[data-testid="cloud-init-yaml"] textarea').element
    ).toHaveProperty("value", "");
    expect(getTextareaStub(wrapper, "cloud-init-yaml").props("errorMessages")).not.toBe("");
  });

  it("cloud-initを無効化するとAPI payloadをnullに戻す", async () => {
    const wrapper = await mountDialog();
    await toggleCloudInit(wrapper, true);
    expect(getCheckboxStub(wrapper, "cloud-init-toggle").props("modelValue")).toBe(true);
    await toggleCloudInit(wrapper, false);
    expect(getCheckboxStub(wrapper, "cloud-init-toggle").props("modelValue")).toBe(false);

    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.apiPost).toHaveBeenCalledOnce();
    expect(mocks.apiPost.mock.calls[0][1].body.cloudInit).toBeNull();
  });

  it("現在usernameの完全一致だけから保存鍵を取得し、自動選択しない", async () => {
    mocks.apiGet.mockResolvedValue({
      data: {
        count: 2,
        data: [
          {
            username: "alice-admin",
            scopes: [],
            projects: [],
            publickeys: [{ name: "wrong", publickey: "ssh-ed25519 WRONG" }],
          },
          {
            username: "alice",
            scopes: [],
            projects: [],
            publickeys: [
              { name: "laptop", publickey: "ssh-ed25519 AAAA laptop" },
              { name: "desktop", publickey: "ssh-ed25519 BBBB desktop" },
            ],
          },
        ],
      },
    });
    const wrapper = await mountDialog();

    await toggleCloudInit(wrapper, true);
    const select = getSelectStub(wrapper, "cloud-init-saved-public-keys");

    expect(mocks.apiGet).toHaveBeenCalledWith("/api/users", {
      params: { query: { nameLike: "alice", limit: 0, page: 0 } },
    });
    expect(select.props("items")).toEqual([
      { name: "laptop", publickey: "ssh-ed25519 AAAA laptop" },
      { name: "desktop", publickey: "ssh-ed25519 BBBB desktop" },
    ]);
    expect(select.props("modelValue")).toEqual([]);

    await toggleCloudInit(wrapper, false);
    await toggleCloudInit(wrapper, true);
    expect(mocks.apiGet).toHaveBeenCalledOnce();
  });

  it("現在usernameが応答にない場合は保存鍵を空のままにする", async () => {
    mocks.apiGet.mockResolvedValue({
      data: {
        count: 1,
        data: [
          {
            username: "alice-admin",
            scopes: [],
            projects: [],
            publickeys: [{ name: "wrong", publickey: "ssh-ed25519 WRONG" }],
          },
        ],
      },
    });
    const wrapper = await mountDialog();

    await toggleCloudInit(wrapper, true);

    expect(getSelectStub(wrapper, "cloud-init-saved-public-keys").props("items")).toEqual([]);
    expect(wrapper.find('[data-testid="saved-public-keys-error"]').exists()).toBe(false);
  });

  it("保存鍵APIの失敗を警告して手入力を妨げない", async () => {
    mocks.apiGet.mockResolvedValue({
      error: {
        detail: {
          code: "service_unavailable",
          message: "The service is temporarily unavailable.",
        },
      },
    });
    const wrapper = await mountDialog();

    await toggleCloudInit(wrapper, true);

    expect(getSelectStub(wrapper, "cloud-init-saved-public-keys").props("items")).toEqual([]);
    expect(wrapper.get('[data-testid="saved-public-keys-error"]').text()).toContain(
      "could not be loaded"
    );

    setLocale("ja");
    await nextTick();
    expect(wrapper.get('[data-testid="saved-public-keys-error"]').text()).toContain(
      "取得できませんでした"
    );
    expect(wrapper.find('[data-testid="cloud-init-manual-public-keys"] textarea').exists()).toBe(true);
  });
});
