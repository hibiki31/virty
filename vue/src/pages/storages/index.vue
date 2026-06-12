<template>
  <v-card>
    <storage-add-dialog v-model="stateCreateDialog"></storage-add-dialog>
    <storage-metadata-edit v-model="stateEditDialog" :uuid="stateEditUUID"></storage-metadata-edit>
    <storage-delete-dialog v-model="dialogDelete" :item="dataDailogDelete"></storage-delete-dialog>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/storages/' + item.uuid" style="font-family: monospace;">{{ item.uuid }}</router-link>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon color="medium-emphasis" icon="mdi-pencil" class="pr-5"
          @click="stateEditDialog = true; stateEditUUID = item.uuid"></v-icon>
        <v-icon color="medium-emphasis" icon="mdi-delete"
          @click="dataDailogDelete = item; dialogDelete = true"></v-icon>
      </template>
      <template v-slot:item.usage="{ item }">
        <v-progress-linear :color="getAvailableColoer(item.capacity, item.available)" height="20"
          style="min-width:70px; width:100%;" :model-value="(item.capacity - item.available) / item.capacity * 100">
          <strong>{{ item.capacity - item.available }}/{{ item.capacity }} GB</strong>
        </v-progress-linear>
      </template>
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Storages
</route>

<script lang="ts" setup>
import { apiClient } from '@/api'
import notify from '@/composables/notify'

import type { typeListStorageQuery } from '@/composables/storage'
import { initStorageList, getStorageList, getAvailableColoer } from '@/composables/storage'
import type { schemas } from '@/composables/schemas'

const loading = ref(false)
const dialogDelete = ref(false)

const dataDailogDelete = ref<schemas['Storage']>()

const stateCreateDialog = ref(false)
const stateEditDialog = ref(false)
const stateEditUUID = ref('')

const headers = [
  { title: 'Name', value: 'name' },
  { title: 'Node', value: 'nodeName' },
  { title: 'UUID', value: 'uuid' },
  { title: 'Usage   ', value: 'usage' },
  { title: 'Path', value: 'path' },
  { title: 'Rool', value: 'metaData.rool' },
  { title: 'Actions', value: 'actions' }
]

const query = ref<typeListStorageQuery>({
  admin: true,
  limit: 20,
  page: 1
})

const items = ref<schemas['StoragePage']>(initStorageList)

async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

const rescan = () => {
  apiClient.PUT('/api/tasks/images').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", "")
    }
  })
}

async function reload() {
  loading.value = true
  items.value = await getStorageList(query.value)
  loading.value = false
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
})
</script>
