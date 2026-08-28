<template>
  <v-card>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">
      <template #item.projects="{ item }">
        <v-chip
          v-for="project in item.projects"
          :key="project.id"
          class="ma-1"
          size="x-small"
          :to="`/projects/${project.id}`"
        >{{ formatProjectName(project) }}</v-chip>
      </template>
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Users
  requiresAdmin: true
</route>

<script lang="ts" setup>
import { ref } from 'vue'
import { getUserList, initUserList, type UserListQuery } from '@/composables/user'
import { formatProjectName } from '@/composables/project'

const loading = ref(false)
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = [
  { title: 'Name', value: 'username' },
  { title: 'Projects', value: 'projects' },
  { title: 'scopes', value: 'scopes' },
  { title: 'publickeys', value: 'publickeys' },
]

const query = ref<UserListQuery>({
  limit: 20,
  page: 1,
  nameLike: "",
})

const items = ref(initUserList)

async function loadItems({ page = 1, itemsPerPage = 10 }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

async function reload() {
  loading.value = true

  try {
    items.value = await getUserList(query.value)
  } finally {
    loading.value = false
  }
}

useReloadListener(async () => {
  await reload()
})

</script>
