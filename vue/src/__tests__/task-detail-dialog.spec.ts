import TaskDetailDialog from "@/components/tasks/TaskDetailDialog.vue";
import { mount } from "@vue/test-utils";
import { defineComponent } from "vue";
import { describe, expect, it } from "vitest";

const ContainerStub = defineComponent({
  template: "<section><slot /></section>",
});

const CodeFieldStub = defineComponent({
  props: {
    loading: Boolean,
    text: String,
    type: String,
  },
  template: '<pre class="code-field">{{ text }}</pre>',
});

describe("TaskDetailDialog", () => {
  it("taskの主要情報を外部通信なしで表示する", () => {
    const wrapper = mount(TaskDetailDialog, {
      props: {
        modelValue: true,
        item: {
          uuid: "task-1",
          method: "post",
          resource: "vm",
          object: "vm-1",
          postTime: "2026-08-22T12:34:00Z",
          request: { name: "vm-1" },
          message: "created",
          log: "finished",
        },
      },
      global: {
        stubs: {
          CodeFeild: CodeFieldStub,
          VCard: ContainerStub,
          VCardItem: ContainerStub,
          VCardSubtitle: ContainerStub,
          VCardText: ContainerStub,
          VCardTitle: ContainerStub,
          VDialog: ContainerStub,
          VDivider: true,
          VIcon: ContainerStub,
        },
      },
    });

    expect(wrapper.text()).toContain("POST VM VM-1");
    expect(wrapper.text()).toContain("Message");
    expect(wrapper.text()).toContain("Request");
    expect(wrapper.text()).toContain("Log");
    expect(
      wrapper.findAll(".code-field").map((element) => element.text())
    ).toEqual(["created", '{\n  "name": "vm-1"\n}', "finished"]);
  });
});
