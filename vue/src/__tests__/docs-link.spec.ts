import DocsLink from "@/components/DocsLink.vue";
import { mount } from "@vue/test-utils";
import { defineComponent } from "vue";
import { describe, expect, it, vi } from "vitest";

const ButtonStub = defineComponent({
  emits: ["click"],
  template: '<button type="button" @click="$emit(\'click\')"><slot /></button>',
});

describe("DocsLink", () => {
  it("文書をnoopener指定の別tabで開く", async () => {
    const popup = { opener: {} } as Window;
    const open = vi.spyOn(window, "open").mockReturnValue(popup);
    const wrapper = mount(DocsLink, {
      props: { url: "https://example.test/docs" },
      global: {
        stubs: { VBtn: ButtonStub },
      },
    });

    await wrapper.get("button").trigger("click");

    expect(open).toHaveBeenCalledWith(
      "https://example.test/docs",
      "_blank",
      "noopener,noreferrer"
    );
    expect(popup.opener).toBeNull();
  });
});
