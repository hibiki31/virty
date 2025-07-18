<template>
  <v-card>
    <task-detail-dialog v-model="stateDetailDialog" :item="dataDetailDaalog"></task-detail-dialog>
    <v-card-title class="d-flex align-center pe-2">
      <v-icon icon="mdi-checkbox-multiple-marked-outline"></v-icon> &nbsp;
      Task List

      <v-spacer></v-spacer>
      <v-select density="compact" clearable label="Status" v-model="query.status" @update:model-value="reload"
        :items="['finish', 'error', 'init', 'wait', 'incomplete']" variant="solo" width="1" class="pr-3"></v-select>
      <v-select density="compact" clearable label="Resouce" v-model="query.resource" @update:model-value="reload"
        :items="['vm', 'network', 'node', 'storage']" variant="solo" width="1" class="pr-3"></v-select>
      <v-select density="compact" clearable label="Method" v-model="query.method" @update:model-value="reload"
        :items="['post', 'put', 'delete', 'patch']" variant="solo" width="1"></v-select>

    </v-card-title>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      v-model:page="pageState" :items-per-page-options="itemsPerPAgeOption" density="comfortable"
      :items-length="items.count" :loading="loading" item-value="name" @update:options="loadItems">

      <template v-slot:item.status="{ value }">
        <v-chip :color="getStatusColor(value)" :text="value.toUpperCase()" variant="flat" size="x-small"></v-chip>
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
import type { typeListTask, typeListTaskQuery } from '@/composables/task'

import { toJST, getStatusColor, getTaskList, toFixedTow, getMethodColor, getResourceIcon } from '@/composables/task'
import { itemsPerPAgeOption } from '@/composables/table'

const loading = ref(false)
const stateDetailDialog = ref(false)
const dataDetailDaalog = ref<typeListTask["data"][0]>()
const pageState = ref(1)

const query = ref<NonNullable<typeListTaskQuery>>({
  admin: true,
  limit: 20,
  page: 1,
  status: "",
  method: "",
  resource: "",
  object: ""
})


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
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

async function reload() {
  loading.value = true
  items.value = await getTaskList(query.value)
  loading.value = false
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
})
</script>
