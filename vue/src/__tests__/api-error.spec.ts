import { describe, expect, it } from "vitest";

import { formatApiError } from "@/composables/apiError";
import { setLocale } from "@/plugins/i18n";

describe("formatApiError", () => {
  it("uses the selected locale for known envelope codes", () => {
    const error = {
      detail: {
        code: "resource_not_found",
        message: "The raw English fallback.",
      },
    };

    setLocale("en");
    expect(formatApiError(error)).toBe("The requested resource was not found.");

    setLocale("ja");
    expect(formatApiError(error)).toBe("対象のリソースが見つかりません。");
  });

  it("localizes normalized field errors without echoing invalid input", () => {
    const error = {
      detail: {
        code: "validation_error",
        message: "Request validation failed.",
        errors: [
          { field: "body.name", code: "required" },
          { field: "query.limit", code: "less_than_or_equal", params: { limit: 100 } },
        ],
      },
    };

    setLocale("en");
    expect(formatApiError(error)).toBe(
      "Name: This field is required.; Items per page: Enter a value less than or equal to 100.",
    );

    setLocale("ja");
    expect(formatApiError(error)).toBe(
      "名前: 必須項目です。; 1ページの件数: 100以下の値を入力してください。",
    );
  });

  it("preserves the backend fallback for an unknown top-level code", () => {
    setLocale("ja");
    expect(formatApiError({
      detail: { code: "future_error", message: "Future server message" },
    })).toBe("Future server message");
  });

  it("uses a generic localized message for non-envelope failures", () => {
    setLocale("en");
    expect(formatApiError({
      detail: [
        { loc: ["body", "name"], msg: "Name is required", type: "missing" },
        { loc: ["body", "port"], msg: "Port is invalid", type: "value_error" },
      ],
    })).toBe("The API request failed.");
    expect(formatApiError({ detail: "legacy detail" })).toBe("The API request failed.");
    expect(formatApiError(new Error("Network unavailable"))).toBe("The API request failed.");
  });
});
