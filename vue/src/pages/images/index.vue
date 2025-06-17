<template>
  <v-card>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      :items-per-page-options="itemsPerPAgeOption" density="comfortable" :items-length="items.count" :loading="loading"
      item-value="name" @update:options="loadItems">
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Images
</route>

<script lang="ts" setup>
import type { typeListImage } from '@/composables/image'

import { ref, onMounted } from 'vue'
import { useReloadListener } from '@/composables/trigger'

import { apiClient } from '@/api'
import notify from '@/composables/notify'

import { getImageList, initImageList } from '@/composables/image'
import { itemsPerPAgeOption } from '@/composables/table'


const loading = ref(false)
const stateCreateDialog = ref(false)
const itemsPerPage = ref(20)

const headers = [
  { title: 'Name', value: 'name' },
  { title: 'Node', value: 'storage.node.name' },
  { title: 'Pool', value: 'storage.name' },
  { title: 'Capacity', value: 'capacity' },
  { title: 'Allocation', value: 'allocation' },
  { title: 'Domain Name', value: 'domainName' },
  { title: 'Flavor Name', value: 'flavor.name' },
  { title: 'Actions', value: 'actions' }
]


const items = ref<typeListImage>(initImageList)


async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  loading.value = true

  const res = await getImageList(itemsPerPage, page)
  items.value = res

  loading.value = false
}


const rescan = () => {
  apiClient.PUT('/api/tasks/vms').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid || "")
    }
  })
}


async function reload() {
  await loadItems({ page: 1, itemsPerPage: itemsPerPage.value })
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})

</script>
