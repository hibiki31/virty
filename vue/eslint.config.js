import vuetify from "eslint-config-vuetify";

// 既存コードの整形移行はlintの責務と分け、誤りを検出するルールだけを有効にする。
export default vuetify(
  {
    imports: false,
    perfectionist: false,
    pnpm: false,
    stylistic: false,
    unicorn: false,
    vue: { a11y: false },
  },
  {
    rules: {
      "curly": "off",
      "object-shorthand": "off",
      "vue/attributes-order": "off",
      "vue/first-attribute-linebreak": "off",
      "vue/html-closing-bracket-newline": "off",
      "vue/html-closing-bracket-spacing": "off",
      "vue/html-indent": "off",
      "vue/html-quotes": "off",
      "vue/html-self-closing": "off",
      "vue/max-attributes-per-line": "off",
      "vue/order-in-components": "off",
      "vue/script-indent": "off",
      "vue/v-on-style": "off",
      "vue/v-slot-style": "off",
    },
  }
);
