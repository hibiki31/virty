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
import { ref, onMounted } from 'vue'
import { apiClient } from '@/api'
import notify from '@/composables/notify'
import { useReloadListener } from '@/composables/trigger'

import type { typeListImage } from '@/composables/image'
import { getImageList, initImageList } from '@/composables/image'

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

const itemsPerPAgeOption = [
  { value: 10, title: '10' },
  { value: 20, title: '20' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
  { value: 100, title: '100' },
  { value: -1, title: '$vuetify.dataFooter.itemsPerPageAll' }
]

const items = ref<typeListImage>(initImageList)



async function loadItems({ page = 0, itemsPerPage = 10, sortBy = "date" }) {
  console.log(page, itemsPerPage)
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
  items.value = await getImageList(itemsPerPage.value, 1)
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})

</script>
