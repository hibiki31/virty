import {
  getMethodColor,
  getResourceIcon,
  getStatusColor,
  methodTranslation,
  toFixedTow,
} from "@/composables/task";
import { describe, expect, it } from "vitest";

describe("task表示helper", () => {
  it("task methodをHTTP methodへ変換する", () => {
    expect(methodTranslation("post")).toBe("POST");
    expect(methodTranslation("put")).toBe("PUT");
    expect(methodTranslation("delete")).toBe("DELETE");
    expect(methodTranslation("patch")).toBe("PATCH");
    expect(methodTranslation("unknown")).toBeUndefined();
  });

  it("method、status、resourceの表示を選択する", () => {
    expect(getMethodColor("post")).toBe("primary");
    expect(getMethodColor("unknown")).toBe("yellow");
    expect(getStatusColor("finish")).toBe("primary");
    expect(getStatusColor("lost")).toBe("grey");
    expect(getStatusColor(null)).toBe("yellow");
    expect(getResourceIcon("vm")).toBe("mdi-desktop-tower");
    expect(getResourceIcon(undefined)).toBe("mdi-help-rhombus");
  });

  it("実行時間を小数1桁に整形する", () => {
    expect(toFixedTow(1.26)).toBe("1.3");
    expect(toFixedTow(Number.POSITIVE_INFINITY)).toBe(0);
  });
});
