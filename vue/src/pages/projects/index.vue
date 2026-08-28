<template>
  <v-card>
    <project-create-dialog v-if="isAdmin" v-model="createDialog" @created="reload" />
    <v-card-actions>
      <v-btn
        v-if="isAdmin"
        color="primary"
        prepend-icon="mdi-folder-plus-outline"
        size="small"
        variant="flat"
        @click="createDialog = true"
      >CREATE</v-btn>
      <v-spacer />
      <v-text-field
        v-model="query.nameLike"
        density="compact"
        flat
        hide-details
        label="Search"
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
      <template #item.usedMemoryG="{ item }">{{ item.usedMemoryG }} GiB</template>
      <template #item.usedStorageG="{ item }">{{ item.usedStorageG }} GiB</template>
    </v-data-table-server>
  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Projects
</route>

<script lang="ts" setup>
import { ref } from 'vue'
import { hasAdminScope } from '@/composables/auth'
import {
  formatProjectName,
  getProjectList,
  initProjectPage,
  type ProjectListQuery,
  type ProjectPage,
} from '@/composables/project'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const isAdmin = hasAdminScope(auth.scopes)
const createDialog = ref(false)
const loading = ref(false)
const itemsPerPage = ref(20)
const page = ref(1)
const items = ref<ProjectPage>(initProjectPage)
const query = ref<ProjectListQuery>({
  limit: 20,
  page: 1,
  nameLike: '',
})

const headers = [
  { title: 'Project', value: 'name' },
  { title: 'Members', value: 'memberCount' },
  { title: 'vCPU used', value: 'usedCore' },
  { title: 'Memory used', value: 'usedMemoryG' },
  { title: 'Storage used', value: 'usedStorageG' },
]

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
