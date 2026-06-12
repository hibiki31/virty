<template>
  <v-card>
    <image-delete-dialog v-model="stateDeleteDialog" :item="imageSelected"></image-delete-dialog>
    <image-download-dialog v-model="stateCreateDialog"></image-download-dialog>
    <v-card-actions>
      <!-- ボタン -->
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">DOWNLOAD</v-btn>
      <v-btn prepend-icon="mdi-delete" variant="flat" color="error" size="small" @click="stateDeleteDialog = true"
        :disabled="imageSelected.length === 0">DELETE</v-btn>
      <v-spacer></v-spacer>
      <!-- フィルタ -->
      <v-select density="compact" clearable label="Node" v-model="query.nodeName"
        @update:model-value="async () => { queryImtesReload(); reload() }" :items="itemsNodes.data"
        variant="solo-filled" width="1" hide-details flat item-title="name" item-value="name" persistent-placeholder
        class="pr-3"></v-select>
      <v-select density="compact" clearable label="Resouce" v-model="query.poolUuid" @update:model-value="reload"
        :items="itemsStorages.data" variant="solo-filled" width="1" hide-details flat item-value="uuid"
        item-title="name" persistent-placeholder class="pr-3">
        <template v-slot:item="{ props: itemProps, item }">
          <v-list-item v-bind="itemProps" :subtitle="item.raw.nodeName"></v-list-item>
        </template>
      </v-select>
      <v-text-field v-model="query.nameLike" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data" show-select
      v-model="imageSelected" :items-per-page-options="itemsPerPAgeOption" density="comfortable"
      :items-length="items.count" :loading="loading" item-value="name" return-object @update:options="loadItems">
      <template v-slot:item.vm="{ item }">
        <router-link :to="'/vms/' + item.domain?.uuid" class="font-mono">{{ item.domain?.name }}</router-link>
      </template>
    </v-data-table-server>
  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Images
</route>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas'
import type { typeListImage, typeListImageQuery } from '@/composables/image'
import { apiClient } from '@/api'
import notify from '@/composables/notify'
import { getImageList, initImageList } from '@/composables/image'
import { itemsPerPAgeOption } from '@/composables/table'
import type { typeListNode } from '@/composables/nodes'
import { initNodeList, getNode } from '@/composables/nodes'
import { initStorageList, getStorageList } from '@/composables/storage'
import type { typeListStorageQuery } from '@/composables/storage'


const loading = ref(false)
const stateCreateDialog = ref(false)
const stateDeleteDialog = ref(false)

const query = ref<typeListImageQuery>({
  admin: true,
  limit: 20,
  page: 1,
  nodeName: null,
  nameLike: "",
  name: "",
  rool: "",
  poolUuid: null,
})

const headers = [

  { title: 'Node', value: 'storage.node.name' },
  { title: 'Pool', value: 'storage.name' },
  { title: 'VM Name', value: 'vm' },
  { title: 'Capacity', value: 'capacity' },
  { title: 'Allocation', value: 'allocation' },
  { title: 'Name', value: 'name' },
  { title: 'Flavor Name', value: 'flavor.name' },
  { title: 'Actions', value: 'actions' }
]

const itemsStorages = ref<schemas['StoragePage']>(initStorageList)
const itemsNodes = ref<typeListNode>(initNodeList)
const items = ref<typeListImage>(initImageList)
const imageSelected = ref<typeListImage["data"]>([])

async function loadItems({ page = 1, itemsPerPage = 10, sortBy = "date" }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}


const rescan = () => {
  apiClient.PUT('/api/tasks/images').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid)
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

useReloadListener(() => {
  reload()
})

async function queryImtesReload() {
  const queryStorage: typeListStorageQuery = {
    admin: true,
    limit: 999999,
    page: 1,
    nodeName: query.value.nodeName
  }
  itemsNodes.value = await getNode()
  itemsStorages.value = await getStorageList(queryStorage)
}

onMounted(async () => {
  await queryImtesReload()
})

</script>
