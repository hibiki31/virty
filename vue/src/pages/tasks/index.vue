<template>
  <v-card>
    <task-detail-dialog v-model="stateDetailDialog" :item="dataDetailDaalog"></task-detail-dialog>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      :items-per-page-options="itemsPerPAgeOption" density="comfortable" :items-length="items.count" :loading="loading"
      item-value="name" @update:options="loadItems">

      <template v-slot:item.status="{ value }">
        <v-chip :color="getStatusColor(value)" :text="value" variant="flat" size="x-small"></v-chip>
      </template>

      <template v-slot:item.postTime="{ value }">
        {{ toJST(value) }}
      </template>

      <template v-slot:item.actions="{ item }">
        <v-icon color="medium-emphasis" icon="mdi-dots-horizontal-circle-outline" size="small"
          @click="dataDetailDaalog = item; stateDetailDialog = true"></v-icon>
      </template>

      <template v-slot:item.runTime="{ value }">
        <div class="text-end">
          {{ toFixedTow(value) }}s
        </div>
      </template>

      <template v-slot:item.uuid="{ value }">
        <div class="font-mono">{{ value }}</div>
      </template>

      <template v-slot:item.resource="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ props }">
            <v-icon v-bind="props" :color="getMethodColor(item.method)">{{ getResourceIcon(item.resource) }}</v-icon>
          </template>
          <span>Json Param: {{ item.request }}</span>
        </v-tooltip>
        <span class="ml-3">{{ item.method }}.{{ item.resource }}.{{ item.object }}</span>
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

import { ref, onMounted } from 'vue'
import { useReloadListener } from '@/composables/trigger'

import { toJST, getStatusColor, getTaskList, toFixedTow, getMethodColor, getResourceIcon } from '@/composables/task'
import { itemsPerPAgeOption } from '@/composables/table'

const loading = ref(false)
const stateCreateDialog = ref(false)
const stateDetailDialog = ref(false)
const dataDetailDaalog = ref<typeListTask["data"][0]>()
const itemsPerPage = ref(20)

const taskError = ref('')


let headers = [
  { title: 'Status', value: 'status' },
  { title: 'PostTime', value: 'postTime' },
  { title: 'userId', value: 'userId' },
  { title: 'Request', value: 'resource' },
  { title: 'ID', value: 'uuid' },
  { title: 'TunTime', value: 'runTime' },
  { title: 'Actions', value: 'actions' }
]


const items = ref<typeListTask>({
  count: 0,
  data: [],
})


async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  loading.value = true
  items.value = await getTaskList(itemsPerPage, page)
  loading.value = false
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
