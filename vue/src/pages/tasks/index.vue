<template>
  <v-card>
    <task-detail-dialog v-model="stateDetailDialog" :item="dataDetailDaalog"></task-detail-dialog>
    <v-card-title class="d-flex align-center pe-2">
      <v-icon icon="mdi-checkbox-multiple-marked-outline"></v-icon> &nbsp;
      {{ t('pages.tasks.heading') }}

      <v-spacer></v-spacer>
      <v-select density="compact" clearable :label="t('pages.tasks.filters.status')" v-model="query.status" @update:model-value="reload"
        :items="taskStatusItems" variant="solo" width="1" class="pr-3"></v-select>
      <v-select density="compact" clearable :label="t('pages.tasks.filters.resource')" v-model="query.resource" @update:model-value="reload"
        :items="taskResourceItems" variant="solo" width="1" class="pr-3"></v-select>
      <v-select density="compact" clearable :label="t('pages.tasks.filters.method')" v-model="query.method" @update:model-value="reload"
        :items="taskMethodItems" variant="solo" width="1"></v-select>

    </v-card-title>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      v-model:page="pageState" :items-per-page-options="itemsPerPAgeOption" density="comfortable"
      :items-length="items.count" :loading="loading" item-value="name" @update:options="loadItems">

      <template v-slot:item.status="{ value }">
        <v-chip :color="getStatusColor(value)" :text="getTaskStatusLabel(value)" variant="flat" size="x-small"></v-chip>
      </template>

      <template v-slot:item.postTime="{ value }">
        {{ formatTaskDateTime(value) }}
      </template>

      <template v-slot:item.actions="{ item }">
        <v-icon color="medium-emphasis" icon="mdi-dots-horizontal-circle-outline" size="small"
          data-testid="task-view-details"
          :aria-label="t('common.actions.viewDetails')" role="button" tabindex="0"
          @click="dataDetailDaalog = item; stateDetailDialog = true"></v-icon>
      </template>

      <template v-slot:item.runTime="{ value }">
        <div class="text-end">
          {{ t('pages.tasks.durationSeconds', { value: formatTaskDuration(value) }) }}
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
          <span>{{ taskRequestLabel(item.request) }}</span>
        </v-tooltip>
        <span class="ml-3">{{ taskMethodLabel(item.method) }}.{{ taskResourceLabel(item.resource) }}.{{ item.object }}</span>
      </template>

    </v-data-table-server>
  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.tasks.documentTitle
</route>

<script lang="ts" setup>
import type { typeListTask, typeListTaskQuery } from '@/composables/task'

import { hasAdminScope } from '@/composables/auth'
import {
  formatTaskDateTime,
  formatTaskDuration,
  getMethodColor,
  getResourceIcon,
  getStatusColor,
  getTaskList,
  taskMethodLabel,
  taskRequestLabel,
  taskResourceLabel,
} from '@/composables/task'
import { itemsPerPAgeOption } from '@/composables/table'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const auth = useAuthStore()
const { t } = useI18n({ useScope: 'global' })
const loading = ref(false)
const stateDetailDialog = ref(false)
const dataDetailDaalog = ref<typeListTask["data"][0]>()
const pageState = ref(1)

const query = ref<NonNullable<typeListTaskQuery>>({
  admin: hasAdminScope(auth.scopes),
  limit: 20,
  page: 1,
  status: "",
  method: "",
  resource: "",
  object: ""
})


const taskStatusValues = ['finish', 'error', 'init', 'wait', 'incomplete'] as const
const taskResourceValues = ['vm', 'network', 'node', 'storage'] as const
const taskMethodValues = ['post', 'put', 'delete', 'patch'] as const

const taskStatusItems = computed(() => taskStatusValues.map(value => ({
  title: t(`pages.tasks.statuses.${value}`),
  value,
})))
const taskResourceItems = computed(() => taskResourceValues.map(value => ({
  title: t(`pages.tasks.resources.${value}`),
  value,
})))
const taskMethodItems = computed(() => taskMethodValues.map(value => ({
  title: t(`pages.tasks.methods.${value}`),
  value,
})))

const getTaskStatusLabel = (value: string) =>
  taskStatusItems.value.find(item => item.value === value)?.title ?? value

const headers = computed(() => [
  { title: t('pages.tasks.columns.status'), value: 'status' },
  { title: t('pages.tasks.columns.postTime'), value: 'postTime' },
  { title: t('pages.tasks.columns.userId'), value: 'userId' },
  { title: t('pages.tasks.columns.request'), value: 'resource' },
  { title: t('pages.tasks.columns.id'), value: 'uuid' },
  { title: t('pages.tasks.columns.runTime'), value: 'runTime' },
  { title: t('pages.tasks.columns.actions'), value: 'actions' }
])


const items = ref<typeListTask>({
  count: 0,
  data: [],
})


async function loadItems({ page = 1, itemsPerPage = 10 }) {
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
