import {
  formatGib,
  formatPercentage,
  getDashboard,
  networkTypeLabel,
  nodeRoleLabel,
  progressPercent,
  ratioPercent,
  taskMethodLabel,
  taskResourceLabel,
  taskStatusLabel,
  utilizationColor,
} from "@/composables/dashboard";
import type {
  DashboardLoadError,
  DashboardResponse,
} from "@/composables/dashboard";
import DashboardPage from "@/pages/index.vue";
import { setLocale } from "@/plugins/i18n";
import { flushPromises, mount } from "@vue/test-utils";
import { defineComponent, nextTick } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  useReloadListener: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: mocks.get,
  },
}));

vi.mock("@/composables/trigger", () => ({
  useReloadListener: mocks.useReloadListener,
}));

const dashboard: DashboardResponse = {
  generatedAt: "2026-08-22T12:34:56Z",
  visibility: "all",
  nodes: {
    count: 3,
    core: 16,
    memoryGib: 48,
    roles: [
      { name: "ssh", count: 3 },
      { name: "libvirt", count: 2 },
    ],
  },
  vms: {
    count: 7,
    core: 12,
    memoryGib: 24,
    statuses: {
      running: 4,
      stopped: 1,
      maintenance: 0,
      deleted: 1,
      lostNode: 1,
      unknown: 0,
    },
  },
  storages: {
    count: 2,
    capacityGib: 1000,
    usedGib: 600,
    availableGib: 400,
    highUsageCount: 1,
    highestUsage: [
      {
        uuid: "storage-1",
        name: "fast-pool",
        nodeName: "node-1",
        capacityGib: 100,
        usedGib: 85,
        availableGib: 15,
        usagePercent: 85,
      },
      {
        uuid: "storage-2",
        name: "archive-pool-with-a-very-long-inventory-display-name",
        nodeName: "node-with-a-very-long-inventory-display-name",
        capacityGib: 0,
        usedGib: 0,
        availableGib: 0,
        usagePercent: null,
      },
    ],
  },
  networks: {
    count: 4,
    portGroupCount: 5,
    types: [
      { name: "bridge", count: 3 },
      { name: "openvswitch", count: 1 },
    ],
  },
  images: { count: 9 },
  tasks: {
    incompleteCount: 2,
    failedLast24Hours: 2,
    recent: [
      {
        uuid: "task-1",
        userId: "operator",
        status: "finish",
        resource: "vm",
        object: "vm-with-a-very-long-inventory-display-name",
        method: "post",
        postTime: "2026-08-22T12:30:00Z",
        runTime: 2.5,
      },
    ],
  },
};

function ok(data: DashboardResponse = dashboard) {
  return {
    data,
    response: new Response(null, { status: 200 }),
  };
}

function failed(status = 503) {
  return {
    error: {
      detail: {
        code: "service_unavailable",
        message: "The service is temporarily unavailable.",
      },
    },
    response: new Response(null, { status }),
  };
}

const ContainerStub = defineComponent({
  inheritAttrs: false,
  template:
    '<div v-bind="$attrs"><slot name="prepend" /><slot /><slot name="append" /></div>',
});

const AlertStub = defineComponent({
  inheritAttrs: false,
  props: {
    text: String,
    title: String,
  },
  template:
    '<div v-bind="$attrs"><strong>{{ title }}</strong><span>{{ text }}</span><slot /><slot name="append" /></div>',
});

const ButtonStub = defineComponent({
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    loading: Boolean,
    to: [String, Object],
  },
  emits: ["click"],
  template:
    '<button v-bind="$attrs" :disabled="disabled" type="button" @click="$emit(\'click\')"><slot /></button>',
});

const CardTitleStub = defineComponent({
  inheritAttrs: false,
  props: { tag: String },
  template:
    '<component :is="tag || \'div\'" v-bind="$attrs"><slot name="prepend" /><slot /><slot name="append" /></component>',
});

const ProgressStub = defineComponent({
  inheritAttrs: false,
  props: { modelValue: Number },
  template: '<div v-bind="$attrs" class="progress-stub"><slot /></div>',
});

const dashboardStubs = {
  VAlert: AlertStub,
  VAvatar: ContainerStub,
  VBtn: ButtonStub,
  VCard: ContainerStub,
  VCardSubtitle: ContainerStub,
  VCardText: ContainerStub,
  VCardTitle: CardTitleStub,
  VChip: ContainerStub,
  VCol: ContainerStub,
  VDivider: ContainerStub,
  VIcon: ContainerStub,
  VList: ContainerStub,
  VListItem: ContainerStub,
  VListItemSubtitle: ContainerStub,
  VListItemTitle: ContainerStub,
  VProgressCircular: ProgressStub,
  VProgressLinear: ProgressStub,
  VRow: ContainerStub,
  VSheet: ContainerStub,
  VSkeletonLoader: ContainerStub,
  VSpacer: ContainerStub,
};

function mountDashboard() {
  return mount(DashboardPage, {
    global: {
      stubs: dashboardStubs,
    },
  });
}

beforeEach(() => {
  mocks.get.mockReset();
  mocks.useReloadListener.mockReset();
});

describe("dashboard APIと表示helper", () => {
  it("typed dashboard snapshotを取得する", async () => {
    mocks.get.mockResolvedValue(ok());

    await expect(getDashboard()).resolves.toBe(dashboard);
    expect(mocks.get).toHaveBeenCalledWith("/api/dashboard");
  });

  it("response dataがない場合はstatus付きerrorにする", async () => {
    mocks.get.mockResolvedValue(failed(503));

    await expect(getDashboard()).rejects.toEqual(
      expect.objectContaining<Partial<DashboardLoadError>>({
        name: "DashboardLoadError",
        status: 503,
      }),
    );
  });

  it("capacityなしとovercommitを安全にpercentへ変換する", () => {
    expect(ratioPercent(3, 4)).toBe(75);
    expect(ratioPercent(3, 0)).toBeNull();
    expect(ratioPercent(Number.NaN, 4)).toBeNull();
    expect(ratioPercent(6, 4)).toBe(150);
    expect(progressPercent(null)).toBe(0);
    expect(progressPercent(150)).toBe(100);
  });

  it("capacity表記と既存storage閾値を揃える", () => {
    expect(formatGib(12.25)).toBe("12.3 GiB");
    expect(formatPercentage(null)).toBe("Unavailable");
    expect(utilizationColor(50)).toBe("primary");
    expect(utilizationColor(80)).toBe("warning");
    expect(utilizationColor(80.1)).toBe("error");
    expect(taskStatusLabel("lost_node")).toBe("lost_node");
  });

  it("既知domain値だけを翻訳し、未知値を変形しない", () => {
    expect(taskStatusLabel("finish")).toBe("Finished");
    expect(taskResourceLabel("vm")).toBe("VM");
    expect(taskMethodLabel("post")).toBe("POST");
    expect(nodeRoleLabel("ssh")).toBe("SSH");
    expect(networkTypeLabel("openvswitch")).toBe("Open vSwitch");
    expect(taskResourceLabel("future_resource")).toBe("future_resource");
    expect(taskMethodLabel("custom_method")).toBe("custom_method");
  });
});

describe("dashboard page", () => {
  it("snapshotから6 KPI、capacity、内訳、注意、recent activityを表示する", async () => {
    mocks.get.mockResolvedValue(ok());
    const wrapper = mountDashboard();

    expect(wrapper.get('[data-testid="dashboard-loading"]').attributes("role")).toBe("status");
    await flushPromises();

    expect(mocks.get).toHaveBeenCalledOnce();
    expect(wrapper.text()).toContain("All VMs and tasks");
    expect(wrapper.findAll(".dashboard-kpi-value").map((item) => item.text())).toEqual([
      "7",
      "3",
      "2",
      "4",
      "9",
      "2",
    ]);
    expect(
      wrapper.findAll(".dashboard-kpi-card").map((item) => item.attributes("to")),
    ).toEqual(["/vms", "/nodes", "/storages", "/networks", "/images", "/tasks"]);
    expect(wrapper.get('[aria-label="Refresh dashboard"]').attributes("title")).toBe(
      "Refresh dashboard",
    );
    expect(wrapper.get(".dashboard-kpi-card").attributes("aria-label")).toBe(
      "Virtual Machines: 7, 4 VMs running. Open Virtual Machines.",
    );
    expect(wrapper.find(".dashboard-hero-subtitle").exists()).toBe(true);
    const sectionHeadings = wrapper.findAll("h2").map((heading) => heading.text());
    for (const heading of [
      "Capacity overview",
      "Virtual machine state",
      "Node roles",
      "Network types",
      "Attention",
      "Recent activity",
    ]) {
      expect(sectionHeadings).toContain(heading);
    }
    const recentHeading = wrapper.get("#recent-activity-heading");
    expect(recentHeading.element.tagName).toBe("H2");
    expect(wrapper.find('section[aria-labelledby="recent-activity-heading"]').exists()).toBe(true);
    const vmStatusText = wrapper.get(".dashboard-status-list").text();
    for (const label of ["Running", "Stopped", "Maintenance", "Lost node", "Deleted", "Unknown"]) {
      expect(vmStatusText).toContain(label);
    }
    expect(wrapper.text()).toContain("Capacity overview");
    expect(wrapper.text()).toContain("vCPU allocation");
    expect(wrapper.text()).toContain("Storage usage");
    expect(wrapper.text()).toContain("75% allocated");
    expect(wrapper.text()).toContain("60% used");
    expect(wrapper.get(".dashboard-metric .progress-stub").attributes("aria-label")).toBe(
      "vCPU allocation: 75%",
    );
    setLocale("ja");
    await nextTick();
    expect(wrapper.get(".dashboard-metric .progress-stub").attributes("aria-label")).toBe(
      "vCPU割り当て: 75%",
    );
    expect(wrapper.text()).toContain("75% 割り当て済み");
    expect(wrapper.text()).toContain("60% 使用済み");
    setLocale("en");
    await nextTick();
    expect(wrapper.text()).toContain("Node roles");
    expect(wrapper.text()).toContain("Network types");
    expect(wrapper.text()).toContain("Failed or lost tasks in the last 24 hours: 2");
    expect(wrapper.text()).toContain("Storage pool at high usage: 1");
    expect(wrapper.text()).toContain("VM that lost its node: 1");
    expect(wrapper.text()).toContain("Deleted VM in inventory: 1");
    expect(wrapper.text()).toContain("Usage unavailable");
    expect(wrapper.text()).not.toContain("Unavailable used");
    expect(wrapper.text()).toContain("POST");
    expect(wrapper.findAll(".dashboard-inline-link")[1].attributes("title")).toBe(
      "archive-pool-with-a-very-long-inventory-display-name",
    );
    expect(wrapper.get(".dashboard-task-object").attributes("title")).toBe(
      "vm-with-a-very-long-inventory-display-name",
    );
    expect(wrapper.get(".dashboard-task-object").classes()).toContain("text-truncate");
  });

  it("empty snapshotを登録導線とrecent activity empty stateで示す", async () => {
    const empty: DashboardResponse = {
      ...dashboard,
      visibility: "assigned",
      nodes: { count: 0, core: 0, memoryGib: 0, roles: [] },
      vms: {
        count: 0,
        core: 0,
        memoryGib: 0,
        statuses: { running: 0, stopped: 0, maintenance: 0, deleted: 0, lostNode: 0, unknown: 0 },
      },
      storages: {
        count: 0,
        capacityGib: 0,
        usedGib: 0,
        availableGib: 0,
        highUsageCount: 0,
        highestUsage: [],
      },
      networks: { count: 0, portGroupCount: 0, types: [] },
      images: { count: 0 },
      tasks: { incompleteCount: 0, failedLast24Hours: 0, recent: [] },
    };
    mocks.get.mockResolvedValue(ok(empty));

    const wrapper = mountDashboard();
    await flushPromises();

    expect(wrapper.get('[data-testid="dashboard-empty"]').text()).toContain(
      "No infrastructure inventory yet",
    );
    expect(wrapper.text()).toContain("Assigned VMs and tasks");
    expect(wrapper.get('[data-testid="recent-activity-empty"]').text()).toContain(
      "No recent activity",
    );
    expect(wrapper.text()).toContain("No dashboard warning indicators are present");
  });

  it("initial errorからretryしてsnapshotを表示する", async () => {
    mocks.get.mockResolvedValueOnce(failed()).mockResolvedValueOnce(ok());
    const wrapper = mountDashboard();
    await flushPromises();

    expect(wrapper.get('[data-testid="dashboard-initial-error"]').text()).toContain(
      "Dashboard unavailable",
    );
    expect(wrapper.get('[data-testid="dashboard-initial-error"]').attributes("role")).toBe("alert");
    expect(wrapper.get('[data-testid="dashboard-initial-error"]').attributes("aria-live")).toBe(
      "assertive",
    );

    const retry = wrapper.findAll("button").find((button) => button.text().includes("Retry"));
    expect(retry).toBeDefined();
    await retry!.trigger("click");
    await flushPromises();

    expect(wrapper.find('[data-testid="dashboard-initial-error"]').exists()).toBe(false);
    expect(wrapper.text()).toContain("Virtual Machines");
  });

  it("refresh失敗時はsnapshotを保持し、stale表示からretryできる", async () => {
    const refreshed = { ...dashboard, images: { count: 10 } } satisfies DashboardResponse;
    mocks.get
      .mockResolvedValueOnce(ok())
      .mockResolvedValueOnce(failed())
      .mockResolvedValueOnce(ok(refreshed));
    const wrapper = mountDashboard();
    await flushPromises();

    await wrapper.get('[aria-label="Refresh dashboard"]').trigger("click");
    await flushPromises();

    expect(wrapper.get('[data-testid="dashboard-stale-alert"]').text()).toContain(
      "Showing the last available snapshot",
    );
    expect(wrapper.findAll(".dashboard-kpi-value")[4].text()).toBe("9");

    const retry = wrapper.findAll("button").find((button) => button.text().includes("Retry"));
    await retry!.trigger("click");
    await flushPromises();

    expect(wrapper.find('[data-testid="dashboard-stale-alert"]').exists()).toBe(false);
    expect(wrapper.findAll(".dashboard-kpi-value")[4].text()).toBe("10");
  });

  it("実行中のmanual refreshと複数task triggerを1回の後続refreshへまとめる", async () => {
    const refreshed = { ...dashboard, images: { count: 11 } } satisfies DashboardResponse;
    let resolveRefresh!: (value: ReturnType<typeof ok>) => void;
    const refresh = new Promise<ReturnType<typeof ok>>((resolve) => {
      resolveRefresh = resolve;
    });
    mocks.get
      .mockResolvedValueOnce(ok())
      .mockReturnValueOnce(refresh)
      .mockResolvedValueOnce(ok(refreshed));
    const wrapper = mountDashboard();
    await flushPromises();

    const listener = mocks.useReloadListener.mock.calls[0][0] as () => void;
    await wrapper.get('[aria-label="Refresh dashboard"]').trigger("click");
    listener();
    listener();
    await nextTick();

    expect(mocks.get).toHaveBeenCalledTimes(2);

    resolveRefresh(ok());
    await flushPromises();
    await flushPromises();

    expect(mocks.get).toHaveBeenCalledTimes(3);
    expect(wrapper.findAll(".dashboard-kpi-value")[4].text()).toBe("11");
  });
});
