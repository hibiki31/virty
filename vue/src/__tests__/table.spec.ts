import { itemsPerPAgeOption } from "@/composables/table";
import { describe, expect, it } from "vitest";

describe("table選択肢", () => {
  it("昇順のpage sizeと全件表示を提供する", () => {
    expect(itemsPerPAgeOption.map(({ value }) => value)).toEqual([
      10,
      20,
      25,
      50,
      100,
      -1,
    ]);
    expect(itemsPerPAgeOption[itemsPerPAgeOption.length - 1]).toEqual({
      value: -1,
      title: "$vuetify.dataFooter.itemsPerPageAll",
    });
  });
});
