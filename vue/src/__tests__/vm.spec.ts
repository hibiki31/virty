import {
  formatStorageCapacity,
  getStorageFileName,
} from "@/composables/vm";
import { describe, expect, it } from "vitest";

describe("VM詳細のstorage表示", () => {
  it("full pathからfile名だけを取り出す", () => {
    expect(getStorageFileName("/var/lib/libvirt/images/example.qcow2")).toBe(
      "example.qcow2"
    );
    expect(getStorageFileName("/var/lib/libvirt/images/")).toBe("images");
  });

  it("容量をGB表記にし、未取得時はplaceholderを返す", () => {
    expect(formatStorageCapacity(32)).toBe("32 GB");
    expect(formatStorageCapacity(0)).toBe("0 GB");
    expect(formatStorageCapacity(null)).toBe("-");
  });
});
