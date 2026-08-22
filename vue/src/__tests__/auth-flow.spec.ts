import {
  removeAuth,
  resolveAuthNavigation,
  setAxios,
} from "@/composables/auth";
import LoginPage from "@/pages/login.vue";
import {
  ButtonStub,
  componentStubs,
  TextFieldStub,
} from "@/__tests__/support/components";
import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  auth: {
    $state: { authed: false, tokenValidated: true },
    loginFailure: vi.fn(),
    loginSuccess: vi.fn(),
    token: "",
  },
  getCookie: vi.fn(),
  notify: vi.fn(),
  removeCookie: vi.fn(),
  route: { query: {} as Record<string, string> },
  routerPush: vi.fn(),
  setCookie: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: {
    GET: mocks.apiGet,
    POST: mocks.apiPost,
  },
}));

vi.mock("@/stores/auth", () => ({
  useAuthStore: () => mocks.auth,
}));

vi.mock("vue-router", () => ({
  useRoute: () => mocks.route,
  useRouter: () => ({ push: mocks.routerPush }),
}));

vi.mock("@kyvg/vue3-notification", () => ({
  useNotification: () => ({ notify: mocks.notify }),
}));

vi.mock("typescript-cookie", () => ({
  getCookie: mocks.getCookie,
  removeCookie: mocks.removeCookie,
  setCookie: mocks.setCookie,
}));

function mountLogin() {
  return mount(LoginPage, {
    global: { stubs: componentStubs },
  });
}

function field(wrapper: ReturnType<typeof mountLogin>, label: string) {
  const target = wrapper
    .findAllComponents(TextFieldStub)
    .find((item) => item.props("label") === label);
  if (!target) throw new Error(`${label} fieldが見つかりません`);
  return target;
}

function loginButton(wrapper: ReturnType<typeof mountLogin>) {
  const target = wrapper
    .findAllComponents(ButtonStub)
    .find((item) => item.text() === "Login");
  if (!target) throw new Error("Login buttonが見つかりません");
  return target;
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.auth.$state.authed = false;
  mocks.auth.$state.tokenValidated = true;
  mocks.auth.token = "";
  mocks.getCookie.mockReturnValue(undefined);
  mocks.route.query = {};
  mocks.routerPush.mockResolvedValue(undefined);
});

describe("認証navigation", () => {
  it("未認証のdeep linkをloginへ送り、認証済みloginはrootへ戻す", () => {
    expect(
      resolveAuthNavigation(false, { path: "/vms/vm-1", fullPath: "/vms/vm-1" }),
    ).toEqual({ path: "/login", query: { redirect: "/vms/vm-1" } });
    expect(
      resolveAuthNavigation(true, { path: "/login", fullPath: "/login" }),
    ).toEqual({ path: "/" });
    expect(
      resolveAuthNavigation(true, { path: "/vms", fullPath: "/vms" }),
    ).toBeUndefined();
  });

  it("管理者限定routeは認証redirect後にadmin scopeを検査する", () => {
    const agentRoute = {
      path: "/agent",
      fullPath: "/agent",
      requiresAdmin: true,
    };

    expect(resolveAuthNavigation(false, agentRoute, [])).toEqual({
      path: "/login",
      query: { redirect: "/agent" },
    });
    expect(resolveAuthNavigation(true, agentRoute, ["user"])).toEqual({
      path: "/",
    });
    expect(
      resolveAuthNavigation(true, agentRoute, ["user", "admin", "vm.read"]),
    ).toBeUndefined();
  });

  it("token cookieを設定・削除する", () => {
    setAxios("token");
    removeAuth();

    expect(mocks.setCookie).toHaveBeenCalledWith("accessToken", "token");
    expect(mocks.removeCookie).toHaveBeenCalledWith("accessToken");
  });

  it("login成功時にcookieを保存して元のdeep linkへ戻る", async () => {
    mocks.route.query = { redirect: "/vms/vm-1" };
    mocks.apiPost.mockResolvedValue({
      data: { access_token: "signed-token", token_type: "bearer" },
    });
    const wrapper = mountLogin();
    await flushPromises();

    await field(wrapper, "ID").get("input").setValue("operator");
    await field(wrapper, "Password").get("input").setValue("password");
    await loginButton(wrapper).trigger("click");
    await flushPromises();

    expect(mocks.setCookie).toHaveBeenCalledWith("accessToken", "signed-token");
    expect(mocks.auth.loginSuccess).toHaveBeenCalledWith("signed-token");
    expect(mocks.routerPush).toHaveBeenCalledWith("/vms/vm-1");
  });

  it("login通信失敗を通知しloadingを必ず解除する", async () => {
    mocks.apiPost.mockRejectedValue(new TypeError("network unavailable"));
    const wrapper = mountLogin();
    await flushPromises();

    await loginButton(wrapper).trigger("click");
    await flushPromises();

    expect(mocks.notify).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "error",
        title: "Login fail",
      }),
    );
    expect(loginButton(wrapper).props("loading")).toBe(false);
  });

  it("保存tokenの検証通信失敗時にcookieと認証stateを破棄する", async () => {
    mocks.getCookie.mockReturnValue("expired-token");
    mocks.apiGet.mockRejectedValue(new TypeError("network unavailable"));

    mountLogin();
    await flushPromises();

    expect(mocks.apiGet).toHaveBeenCalledWith("/api/auth/validate", {
      headers: { Authorization: "Bearer expired-token" },
    });
    expect(mocks.removeCookie).toHaveBeenCalledWith("accessToken");
    expect(mocks.auth.loginFailure).toHaveBeenCalledOnce();
    expect(mocks.notify).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Login Failed", type: "error" }),
    );
  });

  it("保存tokenが401なら期限切れ通知後にcookieと認証stateを破棄する", async () => {
    mocks.getCookie.mockReturnValue("expired-token");
    mocks.apiGet.mockResolvedValue({
      error: { detail: "expired" },
      response: new Response(null, { status: 401 }),
    });

    mountLogin();
    await flushPromises();

    expect(mocks.removeCookie).toHaveBeenCalledWith("accessToken");
    expect(mocks.auth.loginFailure).toHaveBeenCalledOnce();
    expect(mocks.notify).toHaveBeenCalledWith({
      type: "error",
      title: "Login Failed",
      text: "Token have expired",
    });
  });
});
