<template>
  <v-card>
    <node-add-dialog v-if="isAdmin" v-model="dialogAdd"></node-add-dialog>
    <node-key-dialog v-if="isAdmin" v-model="dialogKey"></node-key-dialog>
    <node-delete-dialog v-if="isAdmin" v-model="dialogDelete" :item="dataDailogDelete"></node-delete-dialog>
    <v-card-actions v-if="isAdmin">
      <v-btn prepend-icon="mdi-file-key" variant="flat" color="primary" size="small"
        @click="dialogKey = true">{{ t('pages.nodes.actions.key') }}</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="dialogAdd = true">{{ t('pages.nodes.actions.join') }}</v-btn>
    </v-card-actions>
    <v-data-table v-model:page="pageState" :items="items.data" :loading="loading" :headers="headers" :items-per-page="10" density="comfortable">
      <template v-slot:item.name="{ item }">
        <router-link :to="'/nodes/' + item.name" class="font-mono">{{ item.name }}</router-link>
      </template>
      <template v-slot:item.status="{ item }">
        <v-icon left class="ma-3" :aria-label="nodeStatusLabel(item.status)" :color="getNodeStatusColor(item.status)" role="img">mdi-power-standby</v-icon>
      </template>
      <template v-slot:item.roles="{ item }">
        <v-chip v-for="role in item.roles" :key="role.roleName" :text="translateDomainValue('nodeRole', role.roleName)" variant="flat" color="primary" size="x-small"
          class="ma-1"></v-chip>
      </template>
      <template v-slot:item.core="{ value }">{{ formatNumber(value) }}</template>
      <template v-slot:item.memory="{ value }">{{ formatNumber(value) }}</template>
      <template v-slot:item.actions="{ item }">
        <v-icon v-if="isAdmin" color="medium-emphasis" icon="mdi-delete" :aria-label="t('common.actions.delete')" role="button" tabindex="0"
          @click="dataDailogDelete = item; dialogDelete = true"></v-icon>
      </template>
    </v-data-table>
  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.nodes.documentTitle
  projectFilter: true
</route>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas'
import { apiClient } from '@/api'
import { getNodeStatusColor } from '@/composables/nodes'
import { useI18n } from 'vue-i18n'
import { formatNumber, nodeStatusLabel, translateDomainValue } from '@/composables/i18n'
import { useProjectFilter } from '@/composables/projectFilter'
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n({ useScope: 'global' })

const loading = ref(false)
const auth = useAuthStore()
const isAdmin = hasAdminScope(auth.scopes)
const { projectId } = useProjectFilter()
const pageState = ref(1)

const dialogAdd = ref(false)
const dialogKey = ref(false)
const dialogDelete = ref(false)

const dataDailogDelete = ref<schemas["Node"]>()

const headers = computed(() => [
  { title: t('pages.nodes.columns.status'), value: 'status' },
  { title: t('pages.nodes.columns.name'), value: 'name' },
  { title: t('pages.nodes.columns.ip'), value: 'domain' },
  { title: t('pages.nodes.columns.port'), value: 'port' },
  { title: t('pages.nodes.columns.core'), value: 'core' },
  { title: t('pages.nodes.columns.memory'), value: 'memory' },
  { title: t('pages.nodes.columns.cpu'), value: 'cpuGen' },
  { title: t('pages.nodes.columns.os'), value: 'osName' },
  { title: t('pages.nodes.columns.qemu'), value: 'qemuVersion' },
  { title: t('pages.nodes.columns.libvirt'), value: 'libvirtVersion' },
  { title: t('pages.nodes.columns.roles'), value: 'roles' },
  { title: t('pages.nodes.columns.actions'), value: 'actions' }
])

const items = ref<schemas['NodePage']>({
  count: 0,
  data: [],
})

const reload = () => {
  apiClient.GET('/api/nodes', {
    params: {
      query: {
        admin: hasAdminScope(auth.scopes),
        limit: 100,
        projectId: projectId.value,
      }
    }
  }).then((res) => {
    if (res.data) {
      items.value = res.data
    }
  })
}

watch(projectId, () => {
  pageState.value = 1
  reload()
})

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})

</script>
