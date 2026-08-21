import {
  intValueRestrictions,
  isValidIp,
  isValidURL,
  limitLength16,
  limitLength32,
  portTCP,
  required,
  vlan,
} from "@/composables/rules";
import { describe, expect, it } from "vitest";

describe("入力規則", () => {
  it("必須値と文字数の境界を判定する", () => {
    expect(required("")).toBe("Required.");
    expect(required("virty")).toBe(true);
    expect(limitLength16("a".repeat(16))).toBe(true);
    expect(limitLength16("a".repeat(17))).toBe("16 characters maximum.");
    expect(limitLength32("a".repeat(33))).toBe("32 characters maximum.");
  });

  it("整数、TCP port、VLANの境界を判定する", () => {
    expect(intValueRestrictions("10")).toBe(true);
    expect(intValueRestrictions("10.5")).toBe("Only Int value");
    expect(portTCP(0)).toBe(true);
    expect(portTCP(65535)).toBe(true);
    expect(portTCP(65536)).toBe("Only tcp port 0~65535");
    expect(vlan(1)).toBe(true);
    expect(vlan(4094)).toBe(true);
    expect(vlan(4095)).toBe("Only vlan 1~4094");
  });

  it("IP addressとURLを検証する", () => {
    expect(isValidIp("192.0.2.1")).toBe(true);
    expect(isValidIp("999.0.2.1")).toBe("Invalid IP format");
    expect(isValidURL("https://example.com/path")).toBe(true);
    expect(isValidURL("not a url")).toBe("not a valid URL.");
  });
});
