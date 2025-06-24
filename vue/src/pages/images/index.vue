<template>
  <v-card>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
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
import type { typeListImage, typeListImageQuery } from '@/composables/image'

import { useReloadListener } from '@/composables/trigger'

import { apiClient } from '@/api'
import notify from '@/composables/notify'

import { getImageList, initImageList } from '@/composables/image'
import { itemsPerPAgeOption } from '@/composables/table'


const loading = ref(false)
const stateCreateDialog = ref(false)

const query = ref<typeListImageQuery>({
  admin: true,
  limit: 20,
  page: 1,
  nodeName: "",
  nameLike: "",
  name: "",
  rool: "",

})

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
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}


const rescan = () => {
  apiClient.PUT('/api/tasks/vms').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid || "")
    }
  })
}


async function reload() {
  loading.value = true
  items.value = await getImageList(query.value)
  loading.value = false
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})

</script>
