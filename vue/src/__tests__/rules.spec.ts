import { mount } from "@vue/test-utils";
import { defineComponent, nextTick } from "vue";
import { describe, expect, it } from "vitest";

import {
  intValueRestrictions,
  isValidIp,
  isValidURL,
  limitLength16,
  limitLength32,
  localizeRule,
  portTCP,
  required,
  useLocalizedRules,
  vlan,
} from "@/composables/rules";
import { setLocale } from "@/plugins/i18n";
import { TextFieldStub } from "@/__tests__/support/components";

describe("入力規則", () => {
  it("pure ruleは完成済み文言ではなくtranslation refを返す", () => {
    expect(required("")).toEqual({ kind: "translation", key: "validation.required" });
    expect(required("virty")).toBe(true);
    expect(limitLength16("a".repeat(16))).toBe(true);
    expect(limitLength16("a".repeat(17))).toEqual({
      kind: "translation",
      key: "validation.maxLength",
      params: { max: 16 },
    });
    expect(limitLength32("a".repeat(33))).toEqual(expect.objectContaining({
      key: "validation.maxLength",
      params: { max: 32 },
    }));
  });

  it("整数、TCP port、VLANの境界を判定する", () => {
    expect(intValueRestrictions("10")).toBe(true);
    expect(intValueRestrictions("10.5")).toEqual(expect.objectContaining({ key: "validation.integer" }));
    expect(portTCP(0)).toBe(true);
    expect(portTCP(65535)).toBe(true);
    expect(portTCP(65536)).toEqual(expect.objectContaining({ key: "validation.tcpPort" }));
    expect(vlan(1)).toBe(true);
    expect(vlan(4094)).toBe(true);
    expect(vlan(4095)).toEqual(expect.objectContaining({ key: "validation.vlan" }));
  });

  it("IP addressとURLを検証する", () => {
    expect(isValidIp("192.0.2.1")).toBe(true);
    expect(isValidIp("999.0.2.1")).toEqual(expect.objectContaining({ key: "validation.invalidIp" }));
    expect(isValidURL("https://example.com/path")).toBe(true);
    expect(isValidURL("not a url")).toEqual(expect.objectContaining({ key: "validation.invalidUrl" }));
  });

  it("Vuetify adapterは評価時点のlocaleで解決する", () => {
    const localizedRequired = localizeRule(required);
    setLocale("en");
    expect(localizedRequired("")).toBe("This field is required.");
    setLocale("ja");
    expect(localizedRequired("")).toBe("必須項目です。");
  });

  it("locale切替時にVTextFieldへ新しいrule identityと文言を渡す", async () => {
    const Harness = defineComponent({
      setup: () => ({ r: useLocalizedRules() }),
      template: '<v-text-field model-value="" :rules="[r.required]" />',
    });
    const wrapper = mount(Harness, {
      global: { stubs: { VTextField: TextFieldStub } },
    });

    setLocale("en");
    await nextTick();
    expect(wrapper.get(".validation-message").text()).toBe("This field is required.");

    setLocale("ja");
    await nextTick();
    expect(wrapper.get(".validation-message").text()).toBe("必須項目です。");
  });
});
