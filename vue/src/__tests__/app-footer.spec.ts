import AppFooter from "@/components/AppFooter.vue";
import { mount } from "@vue/test-utils";
import { defineComponent } from "vue";
import { describe, expect, it } from "vitest";

const FooterStub = defineComponent({
  template: "<footer><slot /></footer>",
});

describe("AppFooter", () => {
  it("application footerを現在年とともに表示する", () => {
    const wrapper = mount(AppFooter, {
      global: {
        stubs: { VFooter: FooterStub },
      },
    });

    expect(wrapper.get("footer").text()).toContain(
      `2019-${new Date().getFullYear()}`
    );
    expect(wrapper.text()).toContain("hibiki31");
  });
});
