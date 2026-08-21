import { createAuthMiddleware } from "@/api";
import { hasAdminScope } from "@/composables/auth";
import { describe, expect, it } from "vitest";

describe("認証middleware", () => {
  it("request時点のtokenをAuthorization headerへ設定する", async () => {
    let token = "first-token";
    const middleware = createAuthMiddleware(() => token);
    const onRequest = middleware.onRequest;

    expect(onRequest).toBeTypeOf("function");
    if (!onRequest) {
      throw new Error("onRequest middlewareがありません。");
    }

    const firstRequest = new Request("https://example.test/api/tasks");
    const firstResult = await onRequest({ request: firstRequest } as never);
    expect(firstResult).toBe(firstRequest);
    expect(firstRequest.headers.get("Authorization")).toBe(
      "Bearer first-token"
    );

    token = "next-token";
    const nextRequest = new Request("https://example.test/api/tasks");
    await onRequest({ request: nextRequest } as never);
    expect(nextRequest.headers.get("Authorization")).toBe("Bearer next-token");
  });

  it("admin scopeを一覧APIのdrill-down queryへ反映する", () => {
    expect(hasAdminScope(["user"])).toBe(false);
    expect(hasAdminScope(["user", "admin"])).toBe(true);
  });
});
