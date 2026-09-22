<template>
  <v-card>
    <v-m-add-dialog v-model="stateCreateDialog"></v-m-add-dialog>
    <v-m-add-dialog v-if="hasAdminScope(auth.scopes) && stateAdminCreateDialog"
      v-model="stateAdminCreateDialog" admin></v-m-add-dialog>
    <v-card-actions class="flex-wrap ga-2">
      <v-btn prepend-icon="mdi-cached" variant="flat" color="info" size="small" @click="rescan">{{ t('pages.vms.actions.rescan') }}</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        data-testid="vm-create-open"
        @click="stateCreateDialog = true">{{ t('pages.vms.actions.create') }}</v-btn>
      <v-btn v-if="hasAdminScope(auth.scopes)" prepend-icon="mdi-shield-plus" variant="tonal" color="primary" size="small"
        ref="adminCreateButton"
        data-testid="vm-admin-create-open"
        @click="stateAdminCreateDialog = true">{{ t('dialogs.vmAdd.adminTitle') }}</v-btn>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" :label="t('pages.vms.filters.search')" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">

      <template v-slot:item.uuid="{ item }">
        <router-link :to="'/vms/' + item.uuid" class="font-mono">{{ item.uuid }}</router-link>
      </template>

      <template v-slot:item.status="{ item }">
        <v-icon :aria-label="vmStatusLabel(item.status)" :color="getPowerColor(item.status)" role="img">mdi-power</v-icon>
      </template>
      <template v-slot:item.memory="{ item }">
        <v-icon left>mdi-memory</v-icon>
        {{ t('pages.vms.memoryGib', { value: formatNumber(item.memory / 1024) }) }}
      </template>
      <template v-slot:item.core="{ item }">
        <v-icon left>mdi-cpu-64-bit</v-icon>
        {{ t('pages.vms.coreCount', { count: item.core }, item.core) }}
      </template>
      <template #item.ownerProject="{ item }">
        <v-chip v-if="item.ownerProject" size="small" :to="`/projects/${item.ownerProject.id}`">
          {{ formatProjectName(item.ownerProject) }}
        </v-chip>
        <span v-else class="text-medium-emphasis">{{ t('pages.vms.personalLegacy') }}</span>
      </template>

    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.vms.documentTitle
  projectFilter: true
</route>

<script lang="ts" setup>
import type { typeListVM, typeListVMQuery } from '@/composables/vm'
import { initVMList, getVMList } from '@/composables/vm'
import { apiClient } from '@/api'
import { hasAdminScope } from '@/composables/auth'
import notify, { rawTextRef } from '@/composables/notify'
import { translationRef, vmStatusLabel } from '@/composables/i18n'
import { getPowerColor } from '@/composables/vm'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { formatNumber } from '@/composables/i18n'
import { formatProjectName } from '@/composables/project'
import { useProjectFilter } from '@/composables/projectFilter'

const auth = useAuthStore()
const { projectId } = useProjectFilter()
const { t } = useI18n({ useScope: 'global' })
const loading = ref(false)
const stateCreateDialog = ref(false)
const stateAdminCreateDialog = ref(false)
const adminCreateButton = ref<{ $el: HTMLButtonElement } | null>(null)
watch(stateAdminCreateDialog, async open => {
  if (!open) {
    await nextTick()
    adminCreateButton.value?.$el.focus()
  }
})
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = computed(() => [
  { title: t('pages.vms.columns.status'), value: 'status' },
  { title: t('pages.vms.columns.name'), value: 'name' },
  { title: t('pages.vms.columns.node'), value: 'nodeName' },
  { title: t('pages.vms.columns.uuid'), value: 'uuid' },
  { title: t('pages.vms.columns.ram'), value: 'memory' },
  { title: t('pages.vms.columns.cpu'), value: 'core' },
  { title: t('pages.vms.columns.userId'), value: 'ownerUserId' },
  { title: t('pages.vms.columns.project'), value: 'ownerProject' }
])

const query = ref<typeListVMQuery>({
  admin: hasAdminScope(auth.scopes),
  limit: 20,
  page: 1,
  nameLike: "",
  nodeNameLike: "",
  projectId: projectId.value,
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
      notify("success", translationRef('pages.vms.notifications.taskQueued'), rawTextRef(res.data[0].uuid))
    }
  })
}

async function reload() {
  loading.value = true
  items.value = await getVMList(query.value)
  loading.value = false
}

watch(projectId, async value => {
  query.value.projectId = value
  pageState.value = 1
  query.value.page = 1
  await reload()
})

useReloadListener(() => {
  reload()
})

onMounted(() => {
})

</script>
