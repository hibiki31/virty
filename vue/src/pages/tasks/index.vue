<template>
  <v-card>
    <task-detail-dialog :text="taskError" v-model="detailDialog"></task-detail-dialog>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      :items-per-page-options="itemsPerPAgeOption" density="comfortable" :items-length="items.count" :loading="loading"
      item-value="name" @update:options="loadItems">

      <template v-slot:item.status="{ value }">
        <v-chip :border="`${getStatusColor(value)} thin opacity-25`" :color="getStatusColor(value)" :text="value"
          size="small"></v-chip>
      </template>
      <template v-slot:item.postTime="{ value }">
        {{ toJST(value) }}
      </template>

      <template v-slot:item.actions="{ item }">
        <v-icon color="medium-emphasis" icon="mdi-pencil" size="small"
          @click="detailDialog = true; taskError = item.log || ''"></v-icon>
      </template>
    </v-data-table-server>
  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Tasks
</route>

<script lang="ts" setup>
import type { typeListTask } from '@/composables/task'

import { apiClient } from '@/api'
import { useReloadListener } from '@/composables/trigger'

import { toJST, getStatusColor, getTaskList } from '@/composables/task'
import { itemsPerPAgeOption } from '@/composables/table'

const taskError = ref('')
const detailDialog = ref(false)

const loading = ref(false)
const stateCreateDialog = ref(false)
const itemsPerPage = ref(20)

const items = ref<typeListTask>({
  count: 0,
  data: [],
})

let headers = [
  { title: 'Status', value: 'status' },
  { title: 'PostTime', value: 'postTime' },
  { title: 'Request', value: 'resource' },
  { title: 'Method', value: 'method' },
  { title: 'userId', value: 'userId' },
  { title: 'ID', value: 'uuid' },
  { title: 'TunTime', value: 'runTime' },
  { title: 'Actions', value: 'actions' }
]

async function loadItems({ page = 0, itemsPerPage = 10, sortBy = "date" }) {
  loading.value = true
  items.value = await getTaskList(itemsPerPage, page)
  loading.value = false
}

function reload() {
  loadItems({ page: 0, itemsPerPage: itemsPerPage.value })
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})
</script>
