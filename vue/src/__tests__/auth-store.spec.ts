import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "@/stores/auth";

const mocks = vi.hoisted(() => ({
  jwtDecode: vi.fn(),
}));

vi.mock("jwt-decode", () => ({ jwtDecode: mocks.jwtDecode }));

beforeEach(() => {
  setActivePinia(createPinia());
  mocks.jwtDecode.mockReset();
  sessionStorage.clear();
});

describe("auth store", () => {
  it("Agent用granular scopeを保持し、認証失敗時にstateを破棄する", () => {
    mocks.jwtDecode.mockReturnValue({
      exp: 4_102_444_800,
      projects: ["a1b2c3"],
      scopes: ["user", "admin", "identity.manage", "vm.read"],
      sub: "operator",
    });
    const auth = useAuthStore();

    auth.loginSuccess("signed-token");

    expect(auth.grantedScopes).toEqual([
      "user",
      "admin",
      "identity.manage",
      "vm.read",
    ]);
    expect(auth.username).toBe("operator");
    expect(auth.projects).toEqual(["a1b2c3"]);
    expect(auth.authed).toBe(true);
    expect(auth.adminMode).toBe(false);
    expect(auth.canUseAdminMode).toBe(true);
    expect(auth.scopes).not.toContain("admin");
    expect(auth.scopes).toContain("identity.manage");

    auth.setAdminMode(true);
    expect(auth.scopes).toContain("admin");

    auth.loginFailure();

    expect(auth.token).toBe("");
    expect(auth.username).toBe("");
    expect(auth.scopes).toEqual([]);
    expect(auth.projects).toEqual([]);
    expect(auth.tokenValidated).toBe(true);
    expect(auth.authed).toBe(false);
    expect(auth.adminMode).toBe(false);
    expect(sessionStorage.getItem("virty:admin-mode")).toBeNull();
  });

  it("同じtabのtoken復元だけでモードを保持し、新規loginと別利用者では解除する", () => {
    mocks.jwtDecode.mockReturnValue({ sub: "operator", scopes: ["admin"] });
    const auth = useAuthStore();
    auth.loginSuccess("token");
    expect(auth.scopes).toEqual(["user"]);
    auth.setAdminMode(true);
    auth.loginSuccess("token", true);
    expect(auth.adminMode).toBe(true);
    auth.loginSuccess("token");
    expect(auth.adminMode).toBe(false);
    auth.setAdminMode(true);
    mocks.jwtDecode.mockReturnValue({ sub: "other", scopes: ["admin"] });
    auth.loginSuccess("other-token", true);
    expect(auth.adminMode).toBe(false);
  });

  it("保存値が残っていても非管理者は管理者モードへ入れない", () => {
    sessionStorage.setItem("virty:admin-mode", "operator");
    mocks.jwtDecode.mockReturnValue({ sub: "operator", scopes: ["user", "vm.create"] });
    const auth = useAuthStore();
    auth.loginSuccess("token", true);
    auth.setAdminMode(true);
    expect(auth.adminMode).toBe(false);
    expect(auth.canUseAdminMode).toBe(false);
    expect(auth.scopes).toEqual(["user", "vm.create"]);
  });
});
