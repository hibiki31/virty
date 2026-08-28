import ProjectCreateDialog from "@/components/projects/ProjectCreateDialog.vue";
import { componentStubs } from "@/__tests__/support/components";
import { setLocale } from "@/plugins/i18n";
import { flushPromises, mount } from "@vue/test-utils";
import { computed, defineComponent, nextTick, type PropType } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  auth: { username: "alice" },
  createProject: vi.fn(),
  getUserList: vi.fn(),
  notify: vi.fn(),
  notifyTask: vi.fn(),
}));

vi.mock("@/composables/project", () => ({
  createProject: mocks.createProject,
}));

vi.mock("@/composables/user", () => ({
  getUserList: mocks.getUserList,
}));

vi.mock("@/composables/notify", () => ({
  default: mocks.notify,
  notificationContentFromError: (error: unknown) => ({
    kind: "api-error",
    error,
  }),
  notifyTask: mocks.notifyTask,
}));

vi.mock("@/stores/auth", () => ({
  useAuthStore: () => mocks.auth,
}));

const AutocompleteStub = defineComponent({
  name: "VAutocomplete",
  inheritAttrs: false,
  props: {
    items: { type: Array as PropType<unknown[]>, default: () => [] },
    label: String,
    loading: Boolean,
    modelValue: {
      type: Array as PropType<string[]>,
      default: () => [],
    },
    rules: {
      type: Array as PropType<Array<(value: string[]) => true | string>>,
      default: () => [],
    },
  },
  emits: ["update:modelValue"],
  setup(props) {
    const validationMessage = computed(() => {
      for (const rule of props.rules) {
        const result = rule(props.modelValue);
        if (result !== true) return result;
      }
      return "";
    });
    return { validationMessage };
  },
  template: `
    <label v-bind="$attrs">
      {{ label }}
      <span class="project-members-validation">{{ validationMessage }}</span>
    </label>
  `,
});

beforeEach(() => {
  vi.clearAllMocks();
  mocks.auth.username = "alice";
  mocks.getUserList.mockResolvedValue({
    count: 2,
    data: [{ username: "alice" }, { username: "bob" }],
  });
  setLocale("en");
});

describe("ProjectCreateDialog validation", () => {
  it("member validationをtranslation refから解決し、locale変更へ追従する", async () => {
    const wrapper = mount(ProjectCreateDialog, {
      props: { modelValue: false },
      global: {
        stubs: {
          ...componentStubs,
          VAutocomplete: AutocompleteStub,
        },
      },
    });

    await wrapper.setProps({ modelValue: true });
    await flushPromises();
    const members = wrapper.getComponent(AutocompleteStub);

    members.vm.$emit("update:modelValue", []);
    await nextTick();
    expect(wrapper.get(".project-members-validation").text()).toBe(
      "Select at least one member.",
    );

    members.vm.$emit("update:modelValue", ["bob"]);
    await nextTick();
    expect(wrapper.get(".project-members-validation").text()).toBe(
      "Keep the signed-in administrator as a member.",
    );

    setLocale("ja");
    await nextTick();
    expect(wrapper.get(".project-members-validation").text()).toBe(
      "ログイン中の管理者をメンバーに残してください。",
    );
  });
});
