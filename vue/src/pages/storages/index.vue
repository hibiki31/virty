<template>
  <v-card>
    <storage-add-dialog v-model="stateCreateDialog"></storage-add-dialog>
    <storage-metadata-edit v-model="stateEditDialog" :uuid="stateEditUUID"></storage-metadata-edit>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name" @update:options="">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/vms/' + item.uuid" style="font-family: monospace;">{{ item.uuid }}</router-link>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon color="medium-emphasis" icon="mdi-pencil" size="small"
          @click="stateEditDialog = true; stateEditUUID = item.uuid"></v-icon>
      </template>
      <template v-slot:item.available="{ item }">
        <v-progress-linear color="teal-lighten-4" height="20"
          :model-value="(item.capacity - item.available) / item.capacity * 100">
          <strong>{{ item.available }}/{{ item.capacity }} GB</strong>
        </v-progress-linear>
      </template>
      <template v-slot:item.overcommit="{ item }">
        <div class="text-end">
          <strong v-if='(item.capacityCommit - item.allocationCommit - item.available) > 0' class="text-error">
            {{ item.capacityCommit - item.allocationCommit - item.available }} GB
          </strong>
          <strong v-else class="text-primary">
            {{ item.capacityCommit - item.allocationCommit - item.available }} GB
          </strong>
        </div>
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Storages
</route>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { apiClient } from '@/api'
import type { paths } from '@/api/openapi'
import notify from '@/composables/notify'
import { useReloadListener } from '@/composables/trigger'

import type { typeListStorage } from '@/composables/storage'
import { initStorageList, getStorageList } from '@/composables/storage'


const loading = ref(false)
const itemsPerPage = ref(10)

const stateCreateDialog = ref(false)
const stateEditDialog = ref(false)
const stateEditUUID = ref('')

const headers = [
  { title: 'Name', value: 'name' },
  { title: 'Node', value: 'nodeName' },
  { title: 'UUID', value: 'uuid' },
  { title: 'Available', value: 'available' },
  { title: 'Over', value: 'overcommit' },
  { title: 'Path', value: 'path' },
  { title: 'Device', value: 'metaData.deviceType' },
  { title: 'Protocol', value: 'metaData.protocol' },
  { title: 'Rool', value: 'metaData.rool' },
  { title: 'Actions', value: 'actions' }
]

const items = ref<typeListStorage>({
  count: 0,
  data: [],
})


const rescan = () => {
  apiClient.PUT('/api/tasks/images').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", "")
    }
  })
}


async function reload() {
  items.value = await getStorageList()
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})

</script>
