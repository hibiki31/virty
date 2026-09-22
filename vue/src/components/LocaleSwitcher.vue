<template>
  <v-menu v-if="compact">
    <template #activator="{ props: activatorProps }">
      <v-btn
        v-bind="activatorProps"
        :aria-label="t('localeSwitcher.label')"
        :data-testid="`${testId}-compact`"
        icon="mdi-translate"
        variant="text"
      />
    </template>
    <v-list density="compact">
      <v-list-item
        v-for="item in localeItems"
        :key="item.value"
        :active="item.value === selectedLocale"
        :data-testid="`locale-switcher-option-${item.value}`"
        :title="item.title"
        @click="selectLocale(item.value)"
      />
    </v-list>
  </v-menu>
  <v-select
    v-else
    v-model="selectedLocale"
    :aria-label="t('localeSwitcher.label')"
    :items="localeItems"
    class="locale-switcher"
    :data-testid="testId"
    density="compact"
    hide-details
    item-title="title"
    item-value="value"
    variant="plain"
  >
    <template #item="{ props: itemProps, item }">
      <v-list-item
        v-bind="itemProps"
        :data-testid="`locale-switcher-option-${item.value}`"
        :title="item.title"
      />
    </template>
  </v-select>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { setLocale, type SupportedLocale } from "@/plugins/i18n";

const {
  compact = false,
  testId = "locale-switcher",
} = defineProps<{ compact?: boolean; testId?: string }>();

const { locale, t } = useI18n({ useScope: "global" });

const localeItems = computed<{ title: string; value: SupportedLocale }[]>(() => [
  { title: t("localeSwitcher.english"), value: "en" },
  { title: t("localeSwitcher.japanese"), value: "ja" },
]);

const selectedLocale = computed<SupportedLocale>({
  get: () => locale.value as SupportedLocale,
  set: value => setLocale(value, true),
});

function selectLocale(locale: SupportedLocale): void {
  setLocale(locale, true);
}
</script>

<style scoped>
.locale-switcher {
  flex: 0 0 8rem;
  max-width: 8rem;
}
</style>
