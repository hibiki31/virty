<template>
  <v-card>
    <project-create-dialog v-if="isAdmin" v-model="createDialog" @created="reload" />
    <v-card-actions>
      <v-btn
        v-if="isAdmin"
        color="primary"
        data-testid="project-create-open"
        prepend-icon="mdi-folder-plus-outline"
        size="small"
        variant="flat"
        @click="createDialog = true"
      >{{ t('common.actions.create') }}</v-btn>
      <v-spacer />
      <v-text-field
        v-model="query.nameLike"
        density="compact"
        flat
        hide-details
        :label="t('pages.projects.filters.search')"
        prepend-inner-icon="mdi-magnify"
        single-line
        variant="solo-filled"
        @update:model-value="reload"
      />
    </v-card-actions>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      :headers="headers"
      :items="items.data"
      :items-length="items.count"
      :loading="loading"
      item-value="id"
      @update:options="loadItems"
    >
      <template #item.name="{ item }">
        <router-link :to="`/projects/${item.id}`">{{ formatProjectName(item) }}</router-link>
      </template>
      <template #item.memberCount="{ item }">{{ formatNumber(item.memberCount) }}</template>
      <template #item.usedCore="{ item }">{{ formatNumber(item.usedCore) }}</template>
      <template #item.usedMemoryG="{ item }">{{ t('pages.projects.gibValue', { value: formatNumber(item.usedMemoryG) }) }}</template>
      <template #item.usedStorageG="{ item }">{{ t('pages.projects.gibValue', { value: formatNumber(item.usedStorageG) }) }}</template>
    </v-data-table-server>
  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.projects.documentTitle
</route>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { hasAdminScope } from '@/composables/auth'
import {
  formatProjectName,
  getProjectList,
  initProjectPage,
  type ProjectListQuery,
  type ProjectPage,
} from '@/composables/project'
import { useAuthStore } from '@/stores/auth'
import { formatNumber } from '@/composables/i18n'
import { useI18n } from 'vue-i18n'

const auth = useAuthStore()
const { t } = useI18n({ useScope: 'global' })
const isAdmin = hasAdminScope(auth.scopes)
const createDialog = ref(false)
const loading = ref(false)
const itemsPerPage = ref(20)
const page = ref(1)
const items = ref<ProjectPage>(initProjectPage)
const query = ref<ProjectListQuery>({
  admin: isAdmin,
  limit: 20,
  page: 1,
  nameLike: '',
})

const headers = computed(() => [
  { title: t('pages.projects.columns.project'), value: 'name' },
  { title: t('pages.projects.columns.members'), value: 'memberCount' },
  { title: t('pages.projects.columns.vcpuUsed'), value: 'usedCore' },
  { title: t('pages.projects.columns.memoryUsed'), value: 'usedMemoryG' },
  { title: t('pages.projects.columns.storageUsed'), value: 'usedStorageG' },
])

async function loadItems(options: { page?: number; itemsPerPage?: number }) {
  query.value.page = options.page ?? 1
  query.value.limit = options.itemsPerPage ?? 20
  await reload()
}

async function reload() {
  loading.value = true
  try {
    items.value = await getProjectList(query.value)
  } finally {
    loading.value = false
  }
}

useReloadListener(() => { void reload() })
</script>
