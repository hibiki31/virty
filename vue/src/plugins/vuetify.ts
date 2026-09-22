/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

// Composables
import { createVuetify } from "vuetify";
import { createVueI18nAdapter } from "vuetify/locale/adapters/vue-i18n";
import { useI18n } from "vue-i18n";

import i18n from "./i18n";

type VuetifyI18n = Parameters<typeof createVueI18nAdapter>[0]["i18n"];

// Vuetify側のlocale string型へ合わせる境界にだけ変換を限定する。
const vuetifyI18n = i18n as unknown as VuetifyI18n;

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  locale: {
    adapter: createVueI18nAdapter({ i18n: vuetifyI18n, useI18n }),
  },
  theme: {
    themes: {
      light: {
        colors: {
          primary: "#137a7f",
          success: "#22663f",
          error: "#e12885",
        },
      },
    },
  },
  icons: {
    defaultSet: "mdi",
  },
});
