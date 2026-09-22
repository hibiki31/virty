<template>
  <v-card>
    <storage-add-dialog v-model="stateCreateDialog"></storage-add-dialog>
    <storage-metadata-edit v-model="stateEditDialog" :uuid="stateEditUUID"></storage-metadata-edit>
    <storage-delete-dialog v-model="dialogDelete" :item="dataDailogDelete"></storage-delete-dialog>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">{{ t('pages.storages.actions.rescan') }}</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">{{ t('pages.storages.actions.create') }}</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:page="query.page" v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/storages/' + item.uuid" style="font-family: monospace;">{{ item.uuid }}</router-link>
      </template>
      <template v-slot:item.metaData.rool="{ item }">
        {{ storageRoleLabel(item.metaData?.rool) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon color="medium-emphasis" icon="mdi-pencil" class="pr-5" :aria-label="t('common.actions.edit')" role="button" tabindex="0"
          @click="stateEditDialog = true; stateEditUUID = item.uuid"></v-icon>
        <v-icon color="medium-emphasis" icon="mdi-delete" :aria-label="t('common.actions.delete')" role="button" tabindex="0"
          @click="dataDailogDelete = item; dialogDelete = true"></v-icon>
      </template>
      <template v-slot:item.usage="{ item }">
        <v-progress-linear :color="getAvailableColoer(item.capacity, item.available)" height="20"
          style="min-width:70px; width:100%;" :model-value="(item.capacity - item.available) / item.capacity * 100">
          <strong>{{ t('pages.storages.capacityGb', {
            used: formatNumber(item.capacity - item.available),
            capacity: formatNumber(item.capacity),
          }) }}</strong>
        </v-progress-linear>
      </template>
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.storages.documentTitle
  projectFilter: true
</route>

<script lang="ts" setup>
import { apiClient } from '@/api'
import notify, { rawTextRef } from '@/composables/notify'
import { formatNumber, storageRoleLabel, translationRef } from '@/composables/i18n'

import type { typeListStorageQuery } from '@/composables/storage'
import { initStorageList, getStorageList, getAvailableColoer } from '@/composables/storage'
import type { schemas } from '@/composables/schemas'
import { useI18n } from 'vue-i18n'
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'
import { useProjectFilter } from '@/composables/projectFilter'

const { t } = useI18n({ useScope: 'global' })

const loading = ref(false)
const auth = useAuthStore()
const isAdmin = hasAdminScope(auth.scopes)
const { projectId } = useProjectFilter()
const dialogDelete = ref(false)

const dataDailogDelete = ref<schemas['Storage']>()

const stateCreateDialog = ref(false)
const stateEditDialog = ref(false)
const stateEditUUID = ref('')

const headers = computed(() => [
  { title: t('pages.storages.columns.name'), value: 'name' },
  { title: t('pages.storages.columns.node'), value: 'nodeName' },
  { title: t('pages.storages.columns.uuid'), value: 'uuid' },
  { title: t('pages.storages.columns.usage'), value: 'usage' },
  { title: t('pages.storages.columns.path'), value: 'path' },
  { title: t('pages.storages.columns.role'), value: 'metaData.rool' },
  { title: t('pages.storages.columns.actions'), value: 'actions' }
])

const query = ref<typeListStorageQuery>({
  admin: isAdmin,
  limit: 20,
  page: 1,
  projectId: projectId.value,
})

const items = ref<schemas['StoragePage']>(initStorageList)

async function loadItems({ page = 1, itemsPerPage = 10 }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

const rescan = () => {
  apiClient.PUT('/api/tasks/images').then((res) => {
    if (res.data) {
      notify("success", translationRef('pages.storages.notifications.taskQueued'), rawTextRef(""))
    }
  })
}

async function reload() {
  loading.value = true
  items.value = await getStorageList(query.value)
  loading.value = false
}

watch(projectId, async value => {
  query.value.projectId = value
  query.value.page = 1
  await reload()
})

useReloadListener(() => {
  reload()
})

onMounted(() => {
})
</script>
