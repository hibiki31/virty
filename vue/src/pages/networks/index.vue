<template>
  <v-card>
    <network-add-dialog v-if="isAdmin" v-model="stateCreateDialog"></network-add-dialog>
    <v-card-actions v-if="isAdmin">
      <v-btn v-if="isAdmin" prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">{{ t('pages.networks.actions.rescan') }}</v-btn>
      <v-btn v-if="isAdmin" prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">{{ t('pages.networks.actions.create') }}</v-btn>
    </v-card-actions>
    <v-data-table-server v-model:page="query.page" v-model:items-per-page="query.limit" :headers="headers" :items="items.data"
      density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="{
          path: `/networks/${item.uuid}`,
          query: query.projectId ? { projectId: query.projectId } : {},
        }" style="font-family: monospace;">{{ item.uuid }}</router-link>
      </template>

      <template v-slot:item.type="{ value }">
        {{ translateDomainValue('networkType', value) }}
      </template>
      <template v-slot:item.dhcp="{ value }">
        {{ booleanLabel(value) }}
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.networks.documentTitle
  projectFilter: true
</route>

<script lang="ts" setup>
import { apiClient } from '@/api'
import notify, { rawTextRef } from '@/composables/notify'
import { booleanLabel, translateDomainValue, translationRef } from '@/composables/i18n'

import type { typeListNetwork, typeListNetworkQuery } from '@/composables/network'
import { getNetworkList, initNetworkList } from '@/composables/network'
import { useI18n } from 'vue-i18n'
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'
import { useProjectFilter } from '@/composables/projectFilter'


const loading = ref(false)
const auth = useAuthStore()
const isAdmin = hasAdminScope(auth.scopes)
const { projectId } = useProjectFilter()
const stateCreateDialog = ref(false)

const { t } = useI18n({ useScope: 'global' })

const headers = computed(() => [
  { title: t('pages.networks.columns.name'), value: 'name' },
  { title: t('pages.networks.columns.bridge'), value: 'bridge' },
  { title: t('pages.networks.columns.node'), value: 'nodeName' },
  { title: t('pages.networks.columns.type'), value: 'type' },
  { title: t('pages.networks.columns.uuid'), value: 'uuid' },
  { title: t('pages.networks.columns.dhcp'), value: 'dhcp' },
  { title: t('pages.networks.columns.actions'), value: 'actions' }
])

const items = ref<typeListNetwork>(initNetworkList)
const query = ref<NonNullable<typeListNetworkQuery>>({
  admin: isAdmin,
  limit: 20,
  page: 1,
  projectId: projectId.value,
})


async function loadItems({ page = 1, itemsPerPage = 10 }) {
  query.value.page = page
  query.value.limit = itemsPerPage
  await reload()
}


const rescan = () => {
  apiClient.PUT('/api/tasks/networks').then((res) => {
    if (res.data) {
      notify("success", translationRef('pages.networks.notifications.taskQueued'), rawTextRef(res.data[0].uuid))
    }
  })
}


async function reload() {
  loading.value = true
  items.value = await getNetworkList(query.value)
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
