import {
  getMethodColor,
  getResourceIcon,
  getStatusColor,
  methodTranslation,
  formatTaskRequest,
  formatTaskDuration,
  taskMethodLabel,
  taskRequestLabel,
  taskResourceLabel,
  taskStatusLabel,
} from "@/composables/task";
import { setLocale } from "@/plugins/i18n";
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
    expect(formatTaskDuration(1.26)).toBe("1.3");
    expect(formatTaskDuration(Number.POSITIVE_INFINITY)).toBe("0.0");
  });

  it("既知のtask値だけを翻訳し、未知値を変形しない", () => {
    expect(taskStatusLabel("finish")).toBe("Finished");
    expect(taskResourceLabel("vm")).toBe("VM");
    expect(taskMethodLabel("post")).toBe("POST");
    expect(taskResourceLabel("future_resource")).toBe("future_resource");
    expect(taskMethodLabel("custom_method")).toBe("custom_method");
  });

  it("requestのraw値を文全体keyのparameterとして保持する", () => {
    const request = { opaqueToken: "REQ-UNCHANGED-42" };
    const rawRequest = '{"opaqueToken":"REQ-UNCHANGED-42"}';

    expect(formatTaskRequest(request)).toBe(rawRequest);
    expect(formatTaskRequest("RAW-STRING-UNCHANGED")).toBe("RAW-STRING-UNCHANGED");

    setLocale("en");
    expect(taskRequestLabel(request)).toBe(`JSON parameters: ${rawRequest}`);
    setLocale("ja");
    expect(taskRequestLabel(request)).toBe(`JSONパラメーター: ${rawRequest}`);
  });
});
