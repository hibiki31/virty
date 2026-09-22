import MainAppBer from "@/components/MainAppBer.vue";
import { componentStubs, LocaleSwitcherStub } from "@/__tests__/support/components";
import type * as TaskPollingModule from "@/composables/taskPolling";
import type * as AuthModule from "@/composables/auth";
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  app: { projectId: null, $reset: vi.fn() },
  auth: { authed: true, scopes: ['user'], loginFailure: vi.fn() },
  apiGet: vi.fn(),
  createTaskPoller: vi.fn(),
  notify: vi.fn(),
  poller: { isRunning: vi.fn(), start: vi.fn(), stop: vi.fn() },
  state: {
    showSideDrawer: false,
    task_uuids: [] as string[],
    trigger: vi.fn(),
  },
}));

vi.mock("@/composables/taskPolling", async (importOriginal) => ({
  ...(await importOriginal<typeof TaskPollingModule>()),
  createTaskPoller: mocks.createTaskPoller,
}));
vi.mock("@/stores/auth", () => ({ useAuthStore: () => mocks.auth }));
vi.mock("@/stores/app", () => ({ useAppStore: () => mocks.app }));
vi.mock("vue-router", () => ({
  useRoute: () => ({ fullPath: "/", meta: {}, query: {} }),
  useRouter: () => ({ replace: vi.fn() }),
}));
vi.mock("vuetify", () => ({ useDisplay: () => ({ xs: false }) }));
vi.mock("@/stores/state", () => ({ useStateStore: () => mocks.state }));
vi.mock("@/composables/notify", () => ({ default: mocks.notify }));
vi.mock("@/composables/sleep", () => ({ asyncSleep: vi.fn() }));
vi.mock("@/composables/auth", async importOriginal => ({
  ...await importOriginal<typeof AuthModule>(),
  removeAuth: vi.fn(),
}));
vi.mock("@/api", () => ({ apiClient: { GET: mocks.apiGet } }));

beforeEach(() => {
  vi.clearAllMocks();
  mocks.auth.authed = true;
  mocks.auth.scopes = ["user"];
  mocks.state.task_uuids = [];
  mocks.createTaskPoller.mockReturnValue(mocks.poller);
});

describe("MainAppBer task polling", () => {
  it.each([
    { scopes: ["admin"], admin: true },
    { scopes: ["user"], admin: false },
    { scopes: ["user", "vm.create"], admin: false },
  ])("$scopes のtask取得範囲を権限に合わせる", async ({ scopes, admin }) => {
    mocks.auth.scopes = scopes;
    const snapshot = { count: 0, hash: "empty", uuids: [] };
    mocks.apiGet.mockResolvedValue({ data: snapshot });
    const wrapper = mount(MainAppBer, { global: { stubs: componentStubs } });
    const options = mocks.createTaskPoller.mock.calls[0][0];
    const signal = new AbortController().signal;

    await expect(options.request("previous", signal)).resolves.toEqual(snapshot);
    expect(mocks.apiGet).toHaveBeenCalledWith("/api/tasks/incomplete", {
      params: { query: { referenceHash: "previous", admin } },
      signal,
    });
    wrapper.unmount();
  });

  it("desktop selectorとnarrow向けcompact selectorを排他的なbreakpoint classで配置する", () => {
    const wrapper = mount(MainAppBer, {
      global: { stubs: componentStubs },
    });
    const switchers = wrapper.findAllComponents(LocaleSwitcherStub);

    expect(switchers).toHaveLength(2);
    expect(switchers[0].props("compact")).toBe(false);
    expect(switchers[0].classes()).toEqual(expect.arrayContaining(["d-none", "d-md-flex"]));
    expect(switchers[1].props("compact")).toBe(true);
    expect(switchers[1].classes()).toEqual(expect.arrayContaining(["d-flex", "d-md-none"]));

    wrapper.unmount();
  });

  it("count減少でstate.triggerを1回実行し、unmountでpollerを停止する", () => {
    const wrapper = mount(MainAppBer, {
      global: { stubs: componentStubs },
    });
    const options = mocks.createTaskPoller.mock.calls[0][0];

    expect(mocks.poller.start).toHaveBeenCalledOnce();
    options.onSnapshot({ count: 2, hash: "first", uuids: ["a", "b"] }, 0);
    options.onSnapshot({ count: 1, hash: "second", uuids: ["b"] }, 2);

    expect(mocks.state.task_uuids).toEqual(["b"]);
    expect(mocks.state.trigger).toHaveBeenCalledOnce();
    expect(mocks.notify).toHaveBeenCalledWith(
      "info",
      { kind: "translation", key: "appBar.reload" },
      { kind: "translation", key: "appBar.reloadAfterTask" },
    );

    wrapper.unmount();
    expect(mocks.poller.stop).toHaveBeenCalledOnce();
  });
});
