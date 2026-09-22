<template>
  <v-card>
    <image-delete-dialog v-model="stateDeleteDialog" :item="imageSelected"></image-delete-dialog>
    <image-download-dialog v-model="stateCreateDialog"></image-download-dialog>
    <v-card-actions>
      <!-- ボタン -->
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">{{ t('pages.images.actions.rescan') }}</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">{{ t('pages.images.actions.download') }}</v-btn>
      <v-btn prepend-icon="mdi-delete" variant="flat" color="error" size="small" @click="stateDeleteDialog = true"
        :disabled="imageSelected.length === 0">{{ t('pages.images.actions.delete') }}</v-btn>
      <v-spacer></v-spacer>
      <!-- フィルタ -->
      <v-select density="compact" clearable :label="t('pages.images.filters.node')" v-model="query.nodeName"
        @update:model-value="async () => { queryImtesReload(); reload() }" :items="itemsNodes.data"
        variant="solo-filled" width="1" hide-details flat item-title="name" item-value="name" persistent-placeholder
        class="pr-3"></v-select>
      <v-select density="compact" clearable :label="t('pages.images.filters.resource')" v-model="query.poolUuid" @update:model-value="reload"
        :items="itemsStorages.data" variant="solo-filled" width="1" hide-details flat item-value="uuid"
        item-title="name" persistent-placeholder class="pr-3">
        <template v-slot:item="{ props: itemProps, item }">
          <v-list-item v-bind="itemProps" :subtitle="item.raw.nodeName"></v-list-item>
        </template>
      </v-select>
      <v-text-field v-model="query.nameLike" density="compact" :label="t('pages.images.filters.search')" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:page="query.page" v-model:items-per-page="query.limit" :headers="headers" :items="items.data" show-select
      v-model="imageSelected" :items-per-page-options="itemsPerPAgeOption" density="comfortable"
      :items-length="items.count" :loading="loading" item-value="name" return-object @update:options="loadItems">
      <template v-slot:item.vm="{ item }">
        <router-link :to="'/vms/' + item.domain?.uuid" class="font-mono">{{ item.domain?.name }}</router-link>
      </template>
      <template v-slot:item.capacity="{ value }">{{ formatNumber(value) }}</template>
      <template v-slot:item.allocation="{ value }">{{ formatNumber(value) }}</template>
    </v-data-table-server>
  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.images.documentTitle
  projectFilter: true
</route>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas'
import type { typeListImage, typeListImageQuery } from '@/composables/image'
import { apiClient } from '@/api'
import notify, { rawTextRef } from '@/composables/notify'
import { translationRef } from '@/composables/i18n'
import { getImageList, initImageList } from '@/composables/image'
import { itemsPerPAgeOption } from '@/composables/table'
import type { typeListNode } from '@/composables/nodes'
import { initNodeList, getNode } from '@/composables/nodes'
import { initStorageList, getStorageList } from '@/composables/storage'
import type { typeListStorageQuery } from '@/composables/storage'
import { useI18n } from 'vue-i18n'
import { formatNumber } from '@/composables/i18n'
import { useProjectFilter } from '@/composables/projectFilter'
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'


const loading = ref(false)
const auth = useAuthStore()
const isAdmin = hasAdminScope(auth.scopes)
const { projectId } = useProjectFilter()
const stateCreateDialog = ref(false)
const stateDeleteDialog = ref(false)

const query = ref<typeListImageQuery>({
  admin: isAdmin,
  limit: 20,
  page: 1,
  nodeName: null,
  nameLike: "",
  name: "",
  rool: "",
  poolUuid: null,
  projectId: projectId.value,
})

const { t } = useI18n({ useScope: 'global' })

const headers = computed(() => [
  { title: t('pages.images.columns.node'), value: 'storage.node.name' },
  { title: t('pages.images.columns.pool'), value: 'storage.name' },
  { title: t('pages.images.columns.vmName'), value: 'vm' },
  { title: t('pages.images.columns.capacity'), value: 'capacity' },
  { title: t('pages.images.columns.allocation'), value: 'allocation' },
  { title: t('pages.images.columns.name'), value: 'name' },
  { title: t('pages.images.columns.flavorName'), value: 'flavor.name' },
  { title: t('pages.images.columns.actions'), value: 'actions' }
])

const itemsStorages = ref<schemas['StoragePage']>(initStorageList)
const itemsNodes = ref<typeListNode>(initNodeList)
const items = ref<typeListImage>(initImageList)
const imageSelected = ref<typeListImage["data"]>([])

async function loadItems({ page = 1, itemsPerPage = 10 }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}


const rescan = () => {
  apiClient.PUT('/api/tasks/images').then((res) => {
    if (res.data) {
      notify("success", translationRef('pages.images.notifications.taskQueued'), rawTextRef(res.data[0].uuid))
    }
  })
}


async function reload() {
  loading.value = true
  items.value = await getImageList(query.value)

  const referenceKeys = new Set(
    items.value.data.map((row) => `${row.storageUuid}::${row.name}`),
  );

  imageSelected.value = imageSelected.value.filter((row) => {
    const key = `${row.storageUuid}::${row.name}`;
    const existsInA = referenceKeys.has(key);
    return existsInA;
  });

  loading.value = false
}

watch(projectId, async value => {
  query.value.projectId = value
  query.value.page = 1
  query.value.nodeName = null
  query.value.poolUuid = null
  imageSelected.value = []
  await queryImtesReload()
  await reload()
})

useReloadListener(() => {
  reload()
})

async function queryImtesReload() {
  const queryStorage: typeListStorageQuery = {
    admin: isAdmin,
    limit: 999999,
    page: 1,
    nodeName: query.value.nodeName,
    projectId: query.value.projectId,
  }
  itemsNodes.value = await getNode(query.value.projectId)
  itemsStorages.value = await getStorageList(queryStorage)
}

onMounted(async () => {
  await queryImtesReload()
})

</script>
