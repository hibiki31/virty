<template>
  <v-card>
    <v-card-actions>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - VMs
</route>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas'
import type { paths } from "@/api/openapi";
import { apiClient } from '@/api'

const loading = ref(false)
const stateCreateDialog = ref(false)
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = [
  { title: 'Name', value: 'username' },
  { title: 'Projects', value: 'projects' },
  { title: 'scopes', value: 'scopes' },
  { title: 'publickeys', value: 'publickeys' },
]

const query = ref<NonNullable<paths["/api/networks"]["get"]["parameters"]["query"]>>({
  admin: true,
  limit: 20,
  page: 1,
  nameLike: "",
  nodeNameLike: "",
})

const items = ref<schemas['UserPage']>({ count: 0, data: [] })

async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

async function reload() {
  loading.value = true

  query.value.page = (query.value.page || 1) - 1;
  const res = await apiClient.GET("/api/users", {
    params: {
      query: query.value,
    },
  });

  if (res.data) {
    items.value = res.data;
  } else {
    items.value = { count: 0, data: [] }
  }

  loading.value = false
}

useReloadListener(async () => {
  await reload()
})

</script>
