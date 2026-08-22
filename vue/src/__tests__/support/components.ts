import { defineComponent, h, type Component, type PropType } from "vue";

let formValidity = true;

export function setFormValidity(valid: boolean): void {
  formValidity = valid;
}

export const ContainerStub = defineComponent({
  inheritAttrs: false,
  template:
    '<div v-bind="$attrs"><slot name="prepend" /><slot /><slot name="append" /></div>',
});

export const ButtonStub = defineComponent({
  name: "VBtn",
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    loading: Boolean,
    type: String,
  },
  emits: ["click"],
  setup(props, { emit }) {
    function click(event: MouseEvent): void {
      emit("click", event);
      if (props.type === "submit") {
        event.preventDefault();
        (event.currentTarget as HTMLButtonElement).form?.requestSubmit();
      }
    }

    return { click };
  },
  template: `
    <button
      v-bind="$attrs"
      :disabled="disabled"
      :data-loading="loading"
      :type="type || 'button'"
      @click="click"
    ><slot /></button>
  `,
});

export const FormStub = defineComponent({
  name: "VForm",
  emits: ["submit"],
  setup(_, { emit, slots }) {
    return () =>
      h(
        "form",
        {
          onSubmit(event: Event) {
            event.preventDefault();
            const submitEvent = Object.assign(
              Promise.resolve({ valid: formValidity }),
              { preventDefault() {} },
            );
            emit("submit", submitEvent);
          },
        },
        slots.default?.(),
      );
  },
});

export const TextFieldStub = defineComponent({
  name: "VTextField",
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    label: String,
    loading: Boolean,
    modelValue: {
      type: [String, Number] as PropType<string | number | null>,
    },
    type: String,
  },
  emits: ["change", "keydown", "update:modelValue"],
  template: `
    <label v-bind="$attrs">
      {{ label }}
      <input
        :disabled="disabled"
        :type="type || 'text'"
        :value="modelValue ?? ''"
        @input="$emit('update:modelValue', $event.target.value)"
        @change="$emit('change', $event.target.value)"
        @keydown="$emit('keydown', $event)"
      >
    </label>
  `,
});

export const TextareaStub = defineComponent({
  name: "VTextarea",
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    errorMessages: { type: [String, Array] as PropType<string | string[]> },
    label: String,
    modelValue: String,
  },
  emits: ["update:modelValue"],
  template: `
    <label v-bind="$attrs">
      {{ label }}
      <textarea
        :disabled="disabled"
        :value="modelValue ?? ''"
        @input="$emit('update:modelValue', $event.target.value)"
      ></textarea>
      <span class="error-messages">{{ errorMessages }}</span>
    </label>
  `,
});

export const CheckboxStub = defineComponent({
  name: "VCheckbox",
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    label: String,
    modelValue: Boolean,
  },
  emits: ["update:modelValue"],
  template: `
    <label v-bind="$attrs">
      <input
        type="checkbox"
        :checked="modelValue"
        :disabled="disabled"
        @change="$emit('update:modelValue', $event.target.checked)"
      >
      {{ label }}
    </label>
  `,
});

export const SelectStub = defineComponent({
  name: "VSelect",
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    items: { type: Array as PropType<unknown[]>, default: () => [] },
    label: String,
    loading: Boolean,
    modelValue: { type: null },
  },
  emits: ["update:modelValue"],
  template: '<div v-bind="$attrs" :data-label="label"><slot />{{ label }}</div>',
});

export const componentStubs: Record<string, Component> = {
  CodeFeild: ContainerStub,
  RouterLink: ContainerStub,
  SetupDialog: ContainerStub,
  VAlert: ContainerStub,
  VAppBar: ContainerStub,
  VAppBarNavIcon: ButtonStub,
  VBtn: ButtonStub,
  VCard: ContainerStub,
  VCardActions: ContainerStub,
  VCardItem: ContainerStub,
  VCardSubtitle: ContainerStub,
  VCardText: ContainerStub,
  VCardTitle: ContainerStub,
  VCheckbox: CheckboxStub,
  VChip: ContainerStub,
  VCol: ContainerStub,
  VDialog: ContainerStub,
  VDivider: ContainerStub,
  VForm: FormStub,
  VIcon: ContainerStub,
  VListItem: ContainerStub,
  VProgressCircular: ContainerStub,
  VRow: ContainerStub,
  VSelect: SelectStub,
  VSpacer: ContainerStub,
  VSwitch: CheckboxStub,
  VTable: ContainerStub,
  VTab: ButtonStub,
  VTabs: ContainerStub,
  VTextField: TextFieldStub,
  VTextarea: TextareaStub,
  VToolbar: ContainerStub,
  VToolbarTitle: ContainerStub,
  VWindow: ContainerStub,
  VWindowItem: ContainerStub,
};
