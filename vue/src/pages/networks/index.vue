<template>
  <v-card>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/vms/' + item.uuid" style="font-family: monospace;">{{ item.uuid }}</router-link>
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Networks
</route>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { apiClient } from '@/api'
import notify from '@/composables/notify'
import { useReloadListener } from '@/composables/trigger'

import type { typeListNetwork, typeListNetworkQuery } from '@/composables/network'
import { getNetworkList, initNetworkList } from '@/composables/network'


const loading = ref(false)
const stateCreateDialog = ref(false)

const headers = [
  { title: 'Name', value: 'name' },
  { title: 'bridge', value: 'bridge' },
  { title: 'Node', value: 'nodeName' },
  { title: 'Type', value: 'type' },
  { title: 'UUID', value: 'uuid' },
  { title: 'DHCP', value: 'dhcp' },
  { title: 'actions', value: 'actions' }
]

const items = ref<typeListNetwork>(initNetworkList)
const query = ref<NonNullable<typeListNetworkQuery>>({
  admin: true,
  limit: 20,
  page: 1
})


async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  query.value.page = page
  query.value.limit = itemsPerPage
  await reload()
}


const rescan = () => {
  apiClient.PUT('/api/tasks/networks').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid || "")
    }
  })
}


async function reload() {
  loading.value = true
  items.value = await getNetworkList(query.value)
  loading.value = false
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
})

</script>
