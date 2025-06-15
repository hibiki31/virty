<template>
  <v-card>
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

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Nodes
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
const stateCreateDialog = ref(false)
const itemsPerPage = ref(10)

const headers = [
  { title: 'Name', value: 'name' },
  { title: 'Node', value: 'nodeName' },
  { title: 'UUID', value: 'uuid' },
  { title: 'Capacity', value: 'capacity' },
  { title: 'Used', value: 'used' },
  { title: 'Available', value: 'available' },
  { title: 'OverCommit', value: 'overcommit' },
  { title: 'active', value: 'active' },
  { title: 'auto', value: 'autoStart' },
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
      notify("success", "The task has been queued.", res.data[0].uuid || "")
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
