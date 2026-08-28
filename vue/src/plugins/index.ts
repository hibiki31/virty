/**
 * plugins/index.ts
 *
 * Automatically included in `./src/main.ts`
 */

// Plugins
import vuetify from "./vuetify";
import i18n from "./i18n";
import pinia from "../stores";
import router from "../router";
import hilight from "./highlight";
import Notifications from "@kyvg/vue3-notification";

// Types
import type { App } from "vue";

export function registerPlugins(app: App) {
  app.use(i18n).use(vuetify).use(router).use(pinia).use(Notifications).use(hilight);
}
