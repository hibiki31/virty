<template>
  <v-card>
    <v-m-add-dialog v-model="stateCreateDialog"></v-m-add-dialog>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/vms/' + item.uuid" class="font-mono">{{ item.uuid }}</router-link>
      </template>

      <template v-slot:item.status="{ item }">
        <v-icon :color="getPowerColor(item.status)">mdi-power</v-icon>
      </template>
      <template v-slot:item.memory="{ item }" justify="right">
        <v-icon left>mdi-memory</v-icon>
        {{ item.memory / 1024 }} G
      </template>
      <template v-slot:item.core="{ item }" justify="right">
        <v-icon left>mdi-cpu-64-bit</v-icon>
        {{ item.core }} core
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - VMs
</route>

<script lang="ts" setup>
import type { typeListVM, typeListVMQuery } from '@/composables/vm'
import { initVMList, getVMList } from '@/composables/vm'
import { apiClient } from '@/api'
import notify from '@/composables/notify'
import { useReloadListener } from '@/composables/trigger'
import { getPowerColor } from '@/composables/vm'


const loading = ref(false)
const stateCreateDialog = ref(false)
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = [
  { title: 'Status', value: 'status' },
  { title: 'name', value: 'name' },
  { title: 'node', value: 'nodeName' },
  { title: 'UUID', value: 'uuid' },
  { title: 'RAM', value: 'memory' },
  { title: 'CPU', value: 'core' },
  { title: 'userId', value: 'ownerUserId' },
  { title: 'groupId', value: 'ownerGroupId' }
]

const query = ref<typeListVMQuery>({
  admin: true,
  limit: 20,
  page: 1,
  nameLike: "",
  nodeNameLike: "",
})

const items = ref<typeListVM>(initVMList)

async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

const rescan = () => {
  apiClient.PUT('/api/tasks/vms').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid)
    }
  })
}

async function reload() {
  loading.value = true
  items.value = await getVMList(query.value)
  loading.value = false
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
})

</script>
