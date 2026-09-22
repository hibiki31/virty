<template>
  <v-card :title="t('navigation.resourcePools')">
    <v-card-text>
      <v-alert v-if="error" class="mb-4" type="error" variant="tonal">{{ error }}</v-alert>
      <v-tabs v-model="tab">
        <v-tab value="storage">{{ t('pages.projectDetail.grants.storagePools') }}</v-tab>
        <v-tab value="network">{{ t('pages.projectDetail.grants.networkPools') }}</v-tab>
      </v-tabs>
      <v-tabs-window v-model="tab">
        <v-tabs-window-item value="storage">
          <div class="d-flex justify-end my-3">
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate('storage')">{{ t('common.actions.add') }}</v-btn>
          </div>
          <v-list v-if="storagePools.length" :aria-label="t('pages.projectDetail.grants.storagePools')">
            <v-list-item v-for="pool in storagePools" :key="pool.id"
              :title="`${pool.name} (#${pool.id})`"
              :subtitle="pool.storages.map(item => `${item.storage.name} (${item.storage.nodeName})`).join(', ') || t('common.values.none')">
              <template #append>
                <v-btn :aria-label="`${t('common.actions.edit')}: ${pool.name}`" icon="mdi-pencil-outline" variant="text" @click="openStorage(pool)" />
                <v-btn :aria-label="`${t('common.actions.delete')}: ${pool.name}`" color="error" icon="mdi-delete-outline" variant="text" @click="removeStorage(pool)" />
              </template>
            </v-list-item>
          </v-list>
          <div v-else class="text-medium-emphasis py-4">{{ t('common.values.none') }}</div>
        </v-tabs-window-item>
        <v-tabs-window-item value="network">
          <div class="d-flex justify-end my-3">
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate('network')">{{ t('common.actions.add') }}</v-btn>
          </div>
          <v-list v-if="networkPools.length" :aria-label="t('pages.projectDetail.grants.networkPools')">
            <v-list-item v-for="pool in networkPools" :key="pool.id"
              :title="`${pool.name} (#${pool.id})`"
              :subtitle="networkSummary(pool) || t('common.values.none')">
              <template #append>
                <v-btn :aria-label="`${t('common.actions.edit')}: ${pool.name}`" icon="mdi-pencil-outline" variant="text" @click="openNetwork(pool)" />
                <v-btn :aria-label="`${t('common.actions.delete')}: ${pool.name}`" color="error" icon="mdi-delete-outline" variant="text" @click="removeNetwork(pool)" />
              </template>
            </v-list-item>
          </v-list>
          <div v-else class="text-medium-emphasis py-4">{{ t('common.values.none') }}</div>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
  </v-card>

  <v-dialog v-model="dialog" max-width="640">
    <v-card :title="editingId === null ? t('pages.resourcePools.create') : t('pages.resourcePools.edit')">
      <v-card-text>
        <v-text-field v-model="name" :disabled="editingId !== null" :label="t('common.fields.name')" maxlength="64" />
        <v-select v-if="kind === 'storage'" v-model="selectedStorageIds" multiple chips
          :items="storageOptions" item-title="title" item-value="value"
          :label="t('pages.resourcePools.members')" />
        <v-select v-else v-model="selectedNetworkKeys" multiple chips
          :items="networkOptions" item-title="title" item-value="value"
          :label="t('pages.resourcePools.members')" />
        <v-alert v-if="dialogError" type="error" variant="tonal">{{ dialogError }}</v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">{{ t('common.actions.cancel') }}</v-btn>
        <v-btn color="primary" :disabled="!name.trim()" :loading="saving" @click="save">{{ t('common.actions.save') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<route lang="yaml">
meta:
  titleKey: navigation.resourcePools
  requiresAdmin: true
</route>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/api'
import type { components } from '@/api/openapi'
import { formatNotificationText, notificationContentFromError } from '@/composables/notify'

type StoragePool = components['schemas']['StoragePool']
type NetworkPool = components['schemas']['NetworkPool']
type Storage = components['schemas']['Storage']
type Network = components['schemas']['Network']
type Kind = 'storage' | 'network'

const { t } = useI18n({ useScope: 'global' })
const tab = ref<Kind>('storage')
const kind = ref<Kind>('storage')
const dialog = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const name = ref('')
const error = ref('')
const dialogError = ref('')
const storagePools = ref<StoragePool[]>([])
const networkPools = ref<NetworkPool[]>([])
const storages = ref<Storage[]>([])
const networks = ref<Network[]>([])
const selectedStorageIds = ref<string[]>([])
const selectedNetworkKeys = ref<string[]>([])

const storageOptions = computed(() => storages.value.map(storage => ({
  title: `${storage.name} (${storage.nodeName})`, value: storage.uuid,
})))
const networkOptions = computed(() => networks.value.flatMap(network => [
  { title: `${network.name} (${network.nodeName})`, value: `n:${network.uuid}` },
  ...network.portgroups.map(port => ({
    title: `${network.name} / ${port.name} (${network.nodeName})`,
    value: `p:${network.uuid}:${port.name}`,
  })),
]))

function message(errorValue: unknown): string {
  return errorValue
    ? formatNotificationText(notificationContentFromError(errorValue))
    : t('pages.resourcePools.failed')
}

async function allStorages(): Promise<Storage[]> {
  const result: Storage[] = []
  for (let page = 0; ; page++) {
    const response = await apiClient.GET('/api/storages', { params: { query: { admin: true, page, limit: 100 } } })
    if (!response.data) throw response.error
    result.push(...response.data.data)
    if (result.length >= response.data.count || response.data.data.length === 0) return result
  }
}

async function allNetworks(): Promise<Network[]> {
  const result: Network[] = []
  for (let page = 0; ; page++) {
    const response = await apiClient.GET('/api/networks', { params: { query: { admin: true, page, limit: 100 } } })
    if (!response.data) throw response.error
    result.push(...response.data.data)
    if (result.length >= response.data.count || response.data.data.length === 0) return result
  }
}

async function reload(): Promise<void> {
  error.value = ''
  try {
    const [storageResponse, networkResponse, storageItems, networkItems] = await Promise.all([
      apiClient.GET('/api/storages/pools', { params: { query: { admin: true } } }),
      apiClient.GET('/api/networks/pools', { params: { query: { admin: true } } }),
      allStorages(), allNetworks(),
    ])
    if (!storageResponse.data) throw storageResponse.error
    if (!networkResponse.data) throw networkResponse.error
    storagePools.value = storageResponse.data
    networkPools.value = networkResponse.data
    storages.value = storageItems
    networks.value = networkItems
  } catch (cause) {
    error.value = message(cause)
  }
}

function openCreate(value: Kind): void {
  kind.value = value
  editingId.value = null
  name.value = ''
  selectedStorageIds.value = []
  selectedNetworkKeys.value = []
  dialogError.value = ''
  dialog.value = true
}

function openStorage(pool: StoragePool): void {
  openCreate('storage')
  editingId.value = pool.id
  name.value = pool.name
  selectedStorageIds.value = pool.storages.map(item => item.storage.uuid)
}

function openNetwork(pool: NetworkPool): void {
  openCreate('network')
  editingId.value = pool.id
  name.value = pool.name ?? ''
  selectedNetworkKeys.value = [
    ...pool.networks.map(network => `n:${network.uuid}`),
    ...pool.ports.map(port => `p:${port.network.uuid}:${port.name}`),
  ]
}

function networkSummary(pool: NetworkPool): string {
  return [
    ...pool.networks.map(network => network.name),
    ...pool.ports.map(port => `${port.network.name} / ${port.name}`),
  ].join(', ')
}

async function save(): Promise<void> {
  saving.value = true
  dialogError.value = ''
  try {
    if (kind.value === 'storage') {
      const response = editingId.value === null
        ? await apiClient.POST('/api/storages/pools', { body: { name: name.value.trim(), storageUuids: selectedStorageIds.value } })
        : await apiClient.PATCH('/api/storages/pools', { body: { id: editingId.value, storageUuids: selectedStorageIds.value } })
      if (!response.data) throw response.error
    } else {
      let poolId = editingId.value
      if (poolId === null) {
        const created = await apiClient.POST('/api/networks/pools', { body: { name: name.value.trim() } })
        if (!created.data) throw created.error
        poolId = created.data.id
      }
      const networkUuids = selectedNetworkKeys.value.filter(key => key.startsWith('n:')).map(key => key.slice(2))
      const ports = selectedNetworkKeys.value.filter(key => key.startsWith('p:')).map(key => {
        const separator = key.indexOf(':', 2)
        return { networkUuid: key.slice(2, separator), portName: key.slice(separator + 1) }
      })
      const response = await apiClient.PUT('/api/networks/pools/{pool_id}', {
        params: { path: { pool_id: poolId } }, body: { networkUuids, ports },
      })
      if (!response.data) throw response.error
    }
    dialog.value = false
    await reload()
  } catch (cause) {
    dialogError.value = message(cause)
  } finally {
    saving.value = false
  }
}

async function removeStorage(pool: StoragePool): Promise<void> {
  if (!window.confirm(t('pages.resourcePools.deleteConfirm', { name: pool.name }))) return
  try {
    const response = await apiClient.DELETE('/api/storages/pools/{pool_id}', { params: { path: { pool_id: pool.id } } })
    if (!response.data) throw response.error
    await reload()
  } catch (cause) { error.value = message(cause) }
}

async function removeNetwork(pool: NetworkPool): Promise<void> {
  if (!window.confirm(t('pages.resourcePools.deleteConfirm', { name: pool.name }))) return
  try {
    const response = await apiClient.DELETE('/api/networks/pools/{id}', { params: { path: { id: pool.id } } })
    if (!response.data) throw response.error
    await reload()
  } catch (cause) { error.value = message(cause) }
}

onMounted(() => { void reload() })
</script>
