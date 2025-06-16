<template>
  <v-card>
    <v-m-add-dialog v-model="stateCreateDialog"></v-m-add-dialog>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/vms/' + item.uuid" class="font-mono">{{ item.uuid }}</router-link>
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - VMs
</route>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { apiClient } from '@/api'
import type { paths } from '@/api/openapi'
import notify from '@/composables/notify'
import { useReloadListener } from '@/composables/trigger'


const loading = ref(false)
const stateCreateDialog = ref(false)
const itemsPerPage = ref(10)

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

const items = ref<paths['/api/vms']['get']['responses']['200']['content']['application/json']>({
  count: 0,
  data: [],
})

function loadItems({ page = 0, itemsPerPage = 10, sortBy = "date" }) {
  loading.value = true
  apiClient.GET('/api/vms', {
    params: {
      query: {
        admin: true,
        limit: itemsPerPage,
        page: page,
      }
    }
  }).then((res) => {
    if (res.data) {
      items.value = res.data
    }
    loading.value = false
  })
}


const rescan = () => {
  apiClient.PUT('/api/tasks/vms').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid || "")
    }
  })
}


useReloadListener(() => {
  loadItems({})
})

</script>
