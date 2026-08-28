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

    expect(auth.scopes).toEqual([
      "user",
      "admin",
      "identity.manage",
      "vm.read",
    ]);
    expect(auth.username).toBe("operator");
    expect(auth.projects).toEqual(["a1b2c3"]);
    expect(auth.authed).toBe(true);

    auth.loginFailure();

    expect(auth.token).toBe("");
    expect(auth.username).toBe("");
    expect(auth.scopes).toEqual([]);
    expect(auth.projects).toEqual([]);
    expect(auth.tokenValidated).toBe(true);
    expect(auth.authed).toBe(false);
  });
});
