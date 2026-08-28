<template>
  <v-card>
    <network-add-dialog v-if="isAdmin" v-model="stateCreateDialog"></network-add-dialog>
    <v-card-actions>
      <v-btn v-if="isAdmin" prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn v-if="isAdmin" prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
      <v-spacer />
      <project-filter-select
        :model-value="query.projectId"
        style="max-width: 300px"
        @update:model-value="updateProjectFilter"
      />
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="{
          path: `/networks/${item.uuid}`,
          query: query.projectId ? { projectId: query.projectId } : {},
        }" style="font-family: monospace;">{{ item.uuid }}</router-link>
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Networks
</route>

<script lang="ts" setup>
import { apiClient } from '@/api'
import notify from '@/composables/notify'

import type { typeListNetwork, typeListNetworkQuery } from '@/composables/network'
import { getNetworkList, initNetworkList } from '@/composables/network'
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'


const loading = ref(false)
const auth = useAuthStore()
const isAdmin = hasAdminScope(auth.scopes)
const route = useRoute()
const router = useRouter()
const stateCreateDialog = ref(false)

const headers = [
  { title: 'Name', value: 'name' },
  { title: 'bridge', value: 'bridge' },
  { title: 'Node', value: 'nodeName' },
  { title: 'Type', value: 'type' },
  { title: 'UUID', value: 'uuid' },
  { title: 'DHCP', value: 'dhcp' },
  { title: 'actions', value: 'actions' }
]

const items = ref<typeListNetwork>(initNetworkList)
const query = ref<NonNullable<typeListNetworkQuery>>({
  admin: isAdmin,
  limit: 20,
  page: 1,
  projectId: typeof route.query.projectId === 'string' ? route.query.projectId : null,
})


async function loadItems({ page = 1, itemsPerPage = 10 }) {
  query.value.page = page
  query.value.limit = itemsPerPage
  await reload()
}


const rescan = () => {
  apiClient.PUT('/api/tasks/networks').then((res) => {
    if (res.data) {
      notify("success", "The task has been queued.", res.data[0].uuid)
    }
  })
}


async function reload() {
  loading.value = true
  items.value = await getNetworkList(query.value)
  loading.value = false
}

async function updateProjectFilter(value: string | null) {
  query.value.projectId = value
  query.value.page = 1
  const routeQuery = { ...route.query }
  if (value) routeQuery.projectId = value
  else delete routeQuery.projectId
  await router.replace({ query: routeQuery })
  await reload()
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
})

</script>
