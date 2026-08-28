import { config } from "@vue/test-utils";
import { beforeEach } from "vitest";

import i18n, { setLocale } from "@/plugins/i18n";

config.global.plugins = [i18n];

beforeEach(() => {
  localStorage.clear();
  setLocale("en");
});
