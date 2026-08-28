<template>
  <v-card>
    <v-m-add-dialog v-model="stateCreateDialog"></v-m-add-dialog>
    <v-card-actions>
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">rescan</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
      <v-spacer></v-spacer>
      <project-filter-select
        :model-value="query.projectId"
        class="pr-3"
        style="max-width: 300px"
        @update:model-value="updateProjectFilter"
      />
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
      <template v-slot:item.memory="{ item }">
        <v-icon left>mdi-memory</v-icon>
        {{ item.memory / 1024 }} G
      </template>
      <template v-slot:item.core="{ item }">
        <v-icon left>mdi-cpu-64-bit</v-icon>
        {{ item.core }} core
      </template>
      <template #item.ownerProject="{ item }">
        <v-chip v-if="item.ownerProject" size="small" :to="`/projects/${item.ownerProject.id}`">
          {{ formatProjectName(item.ownerProject) }}
        </v-chip>
        <span v-else class="text-medium-emphasis">Personal / legacy</span>
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
import { hasAdminScope } from '@/composables/auth'
import notify from '@/composables/notify'
import { getPowerColor } from '@/composables/vm'
import { useAuthStore } from '@/stores/auth'
import { formatProjectName } from '@/composables/project'
import { useRoute, useRouter } from 'vue-router'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
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
  { title: 'Project', value: 'ownerProject' }
]

const query = ref<typeListVMQuery>({
  admin: hasAdminScope(auth.scopes),
  limit: 20,
  page: 1,
  nameLike: "",
  nodeNameLike: "",
  projectId: typeof route.query.projectId === 'string' ? route.query.projectId : null,
})

const items = ref<typeListVM>(initVMList)

async function loadItems({ page = 1, itemsPerPage = 10 }) {
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

async function updateProjectFilter(projectId: string | null) {
  query.value.projectId = projectId
  const routeQuery = { ...route.query }
  if (projectId) routeQuery.projectId = projectId
  else delete routeQuery.projectId
  await router.replace({ query: routeQuery })
  pageState.value = 1
  query.value.page = 1
  await reload()
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
})

</script>
