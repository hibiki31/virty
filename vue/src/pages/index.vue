<template>
  <div class="dashboard-page" :aria-busy="isLoading">
    <v-sheet class="dashboard-hero pa-5 pa-sm-7 mb-5" color="primary" rounded="lg">
      <div class="d-flex flex-wrap align-center ga-4">
        <div class="dashboard-hero-icon d-flex align-center justify-center" aria-hidden="true">
          <v-icon icon="mdi-view-dashboard-outline" size="34" />
        </div>
        <div>
          <h1 class="text-h4 font-weight-bold">{{ t('dashboard.title') }}</h1>
          <p class="dashboard-hero-subtitle text-body-2 mt-1 mb-0">
            {{ t('dashboard.subtitle') }}
          </p>
          <div v-if="dashboard" class="d-flex flex-wrap align-center ga-2 mt-3">
            <v-chip color="white" prepend-icon="mdi-eye-outline" size="small" variant="outlined">
              {{ visibilityLabel }}
            </v-chip>
            <span class="dashboard-hero-meta text-caption">
              {{ t('dashboard.updated', { date: formatTimestamp(dashboard.generatedAt) }) }}
            </span>
          </div>
        </div>
        <v-spacer />
        <v-btn
          :disabled="isInitialLoading"
          :loading="isRefreshing"
          :aria-label="t('dashboard.refreshAria')"
          color="white"
          icon="mdi-refresh"
          :title="t('dashboard.refreshAria')"
          variant="tonal"
          @click="loadDashboard"
        />
      </div>
    </v-sheet>

    <div v-if="isInitialLoading" data-testid="dashboard-loading" role="status" aria-live="polite">
      <span class="sr-only">{{ t('dashboard.loading') }}</span>
      <v-row>
        <v-col v-for="index in 6" :key="index" cols="12" sm="6" md="4" xl="2">
          <v-skeleton-loader class="dashboard-kpi-card" type="article" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" lg="7"><v-skeleton-loader type="article, actions" /></v-col>
        <v-col cols="12" lg="5"><v-skeleton-loader type="article, actions" /></v-col>
      </v-row>
    </div>

    <v-card
      v-else-if="!dashboard"
      class="pa-5 pa-sm-8 text-center"
      data-testid="dashboard-initial-error"
      role="alert"
      aria-live="assertive"
      variant="outlined"
    >
      <v-icon color="error" icon="mdi-cloud-alert-outline" size="52" />
      <h2 class="text-h5 mt-4">{{ t('dashboard.unavailableTitle') }}</h2>
      <p class="text-body-2 text-medium-emphasis mx-auto mt-2 dashboard-message-width">
        {{ t('dashboard.unavailableDescription') }}
      </p>
      <v-btn class="mt-5" color="primary" prepend-icon="mdi-refresh" @click="loadDashboard">
        {{ t('common.actions.retry') }}
      </v-btn>
    </v-card>

    <template v-else>
      <v-alert
        v-if="loadError"
        class="mb-5"
        data-testid="dashboard-stale-alert"
        icon="mdi-history"
        :title="t('dashboard.staleTitle')"
        type="warning"
        variant="tonal"
      >
        {{ t('dashboard.staleDescription') }}
        <template #append>
          <v-btn :loading="isRefreshing" size="small" variant="text" @click="loadDashboard">{{ t('common.actions.retry') }}</v-btn>
        </template>
      </v-alert>

      <v-alert
        v-if="isInventoryEmpty"
        class="mb-5"
        data-testid="dashboard-empty"
        icon="mdi-package-variant-closed"
        :title="t('dashboard.noInventoryTitle')"
        type="info"
        variant="tonal"
      >
        {{ t('dashboard.noInventoryDescription') }}
        <template #append>
          <v-btn size="small" to="/nodes" variant="text">{{ t('dashboard.nodesLink') }}</v-btn>
        </template>
      </v-alert>

      <section aria-labelledby="dashboard-overview-heading">
        <h2 id="dashboard-overview-heading" class="sr-only">{{ t('dashboard.overview') }}</h2>
        <v-row>
          <v-col v-for="item in kpis" :key="item.title" cols="12" sm="6" md="4" xl="2">
            <v-card
              :aria-label="t('dashboard.kpiAria', { title: item.title, value: formatNumber(item.value), detail: item.detail })"
              :to="item.to"
              class="dashboard-kpi-card h-100"
              color="primary"
              :data-testid="`dashboard-kpi-${item.to.slice(1)}`"
              variant="tonal"
            >
              <v-card-text class="d-flex align-center ga-4">
                <div class="dashboard-kpi-icon d-flex align-center justify-center" aria-hidden="true">
                  <v-icon :icon="item.icon" size="28" />
                </div>
                <div class="min-width-0">
                  <h3 class="text-caption text-medium-emphasis">{{ item.title }}</h3>
                  <div class="dashboard-kpi-value text-h4 font-weight-bold">{{ formatNumber(item.value) }}</div>
                  <div class="text-caption text-medium-emphasis text-truncate">{{ item.detail }}</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </section>

      <v-row class="mt-1">
        <v-col cols="12" lg="7">
          <v-card class="h-100" variant="outlined">
            <v-card-title class="d-flex align-center ga-2" tag="h2">
              <v-icon color="primary" icon="mdi-gauge" />
              {{ t('dashboard.capacityTitle') }}
            </v-card-title>
            <v-card-subtitle>{{ t('dashboard.capacitySubtitle') }}</v-card-subtitle>
            <v-card-text>
              <div v-for="metric in allocationMetrics" :key="metric.label" class="dashboard-metric mb-5">
                <div class="d-flex justify-space-between ga-4 mb-2">
                  <span class="font-weight-medium">{{ metric.label }}</span>
                  <span class="text-body-2 text-medium-emphasis text-right">{{ metric.summary }}</span>
                </div>
                <v-progress-linear
                  :aria-label="t('dashboard.metricAria', {
                    label: metric.label,
                    value: formatPercentage(metric.percent),
                  })"
                  :color="utilizationColor(metric.percent)"
                  :model-value="progressPercent(metric.percent)"
                  height="10"
                  rounded
                />
                <div class="text-caption text-medium-emphasis mt-1">
                  {{ metric.percentLabel }}
                </div>
              </div>

              <v-divider class="mb-4" />
              <div class="d-flex align-center justify-space-between ga-3 mb-2">
                <h3 class="text-subtitle-1 font-weight-bold">{{ t('dashboard.highestStorageUsage') }}</h3>
                <v-btn size="small" to="/storages" variant="text">{{ t('common.actions.viewAll') }}</v-btn>
              </div>
              <div v-if="dashboard.storages.highestUsage.length === 0" class="text-body-2 text-medium-emphasis py-4">
                {{ t('dashboard.noStorageCapacity') }}
              </div>
              <template v-else>
                <div
                  v-for="storage in dashboard.storages.highestUsage"
                  :key="storage.uuid"
                  class="dashboard-storage-row py-2"
                >
                  <div class="d-flex align-center justify-space-between ga-3 mb-2">
                    <div class="min-width-0">
                      <v-btn
                        :to="`/storages/${storage.uuid}`"
                        class="text-none px-0 dashboard-inline-link"
                        density="compact"
                        :title="storage.name"
                        variant="text"
                      >
                        {{ storage.name }}
                      </v-btn>
                      <div class="text-caption text-medium-emphasis text-truncate">{{ storage.nodeName }}</div>
                    </div>
                    <div class="text-caption text-right">
                      {{ formatGib(storage.usedGib) }} / {{ formatGib(storage.capacityGib) }}
                    </div>
                  </div>
                  <v-progress-linear
                    :aria-label="t('dashboard.storageUsageAria', { name: storage.name, usage: storage.usagePercent === null ? t('dashboard.usageUnavailable') : formatPercentage(storage.usagePercent) })"
                    :color="utilizationColor(storage.usagePercent)"
                    :model-value="progressPercent(storage.usagePercent)"
                    height="8"
                    rounded
                  />
                  <div class="text-caption text-medium-emphasis mt-1">
                    <template v-if="storage.usagePercent === null">{{ t('dashboard.usageUnavailable') }}</template>
                    <template v-else>{{ t('dashboard.percentUsed', { percent: formatPercentage(storage.usagePercent) }) }}</template>
                    · {{ t('dashboard.valueAvailable', { value: formatGib(storage.availableGib) }) }}
                  </div>
                </div>
              </template>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" lg="5">
          <v-card class="h-100" variant="outlined">
            <v-card-title class="d-flex align-center ga-2" tag="h2">
              <v-icon color="primary" icon="mdi-desktop-tower-monitor" />
              {{ t('dashboard.vmStateTitle') }}
            </v-card-title>
            <v-card-subtitle>{{ t('dashboard.vmStateSubtitle') }}</v-card-subtitle>
            <v-card-text>
              <div class="d-flex flex-column flex-sm-row align-center justify-space-around ga-6 py-3">
                <v-progress-circular
                  :aria-label="t('dashboard.runningVmsAria', { percent: formatPercentage(vmRunningPercent) })"
                  :model-value="progressPercent(vmRunningPercent)"
                  color="primary"
                  size="152"
                  width="14"
                >
                  <div class="text-center">
                    <div class="text-h4 font-weight-bold">{{ formatNumber(dashboard.vms.statuses.running) }}</div>
                    <div class="text-caption">{{ t('dashboard.running') }}</div>
                    <div class="text-caption text-medium-emphasis">{{ t('dashboard.ofCount', { count: formatNumber(dashboard.vms.count) }, dashboard.vms.count) }}</div>
                  </div>
                </v-progress-circular>

                <v-list class="dashboard-status-list flex-grow-1" density="compact">
                  <v-list-item v-for="status in vmStatuses" :key="status.label">
                    <template #prepend>
                      <v-icon :color="status.color" :icon="status.icon" size="18" />
                    </template>
                    <v-list-item-title>{{ status.label }}</v-list-item-title>
                    <template #append>
                      <span class="font-weight-bold ms-4">{{ formatNumber(status.count) }}</span>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-1">
        <v-col cols="12" md="6" xl="4">
          <v-card class="h-100" variant="outlined">
            <v-card-title class="d-flex align-center ga-2" tag="h2">
              <v-icon color="primary" icon="mdi-shield-account-outline" />
              {{ t('dashboard.nodeRoles') }}
            </v-card-title>
            <v-card-text>
              <div v-if="dashboard.nodes.roles.length === 0" class="text-body-2 text-medium-emphasis py-4">
                {{ t('dashboard.noNodeRoles') }}
              </div>
              <template v-else>
                <div v-for="role in dashboard.nodes.roles" :key="role.name" class="mb-4">
                  <div class="d-flex justify-space-between mb-2">
                    <span>{{ nodeRoleLabel(role.name) }}</span>
                    <span class="font-weight-bold">{{ formatNumber(role.count) }}</span>
                  </div>
                  <v-progress-linear
                    :aria-label="t('dashboard.roleAria', { role: nodeRoleLabel(role.name), count: formatNumber(role.count) }, role.count)"
                    color="primary"
                    :model-value="progressPercent(ratioPercent(role.count, dashboard.nodes.count))"
                    height="8"
                    rounded
                  />
                </div>
              </template>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6" xl="4">
          <v-card class="h-100" variant="outlined">
            <v-card-title class="d-flex align-center ga-2" tag="h2">
              <v-icon color="primary" icon="mdi-access-point-network" />
              {{ t('dashboard.networkTypes') }}
            </v-card-title>
            <v-card-text>
              <div v-if="dashboard.networks.types.length === 0" class="text-body-2 text-medium-emphasis py-4">
                {{ t('dashboard.noNetworks') }}
              </div>
              <template v-else>
                <div v-for="networkType in dashboard.networks.types" :key="networkType.name" class="mb-4">
                  <div class="d-flex justify-space-between mb-2">
                    <span>{{ networkTypeLabel(networkType.name) }}</span>
                    <span class="font-weight-bold">{{ formatNumber(networkType.count) }}</span>
                  </div>
                  <v-progress-linear
                    :aria-label="t('dashboard.networkAria', { type: networkTypeLabel(networkType.name), count: formatNumber(networkType.count) }, networkType.count)"
                    color="info"
                    :model-value="progressPercent(ratioPercent(networkType.count, dashboard.networks.count))"
                    height="8"
                    rounded
                  />
                </div>
              </template>
              <v-divider v-if="dashboard.networks.types.length > 0" class="mb-3" />
              <div class="d-flex justify-space-between text-body-2">
                <span class="text-medium-emphasis">{{ t('dashboard.portGroups') }}</span>
                <strong>{{ formatNumber(dashboard.networks.portGroupCount) }}</strong>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" xl="4">
          <v-card class="h-100" variant="outlined">
            <v-card-title class="d-flex align-center ga-2" tag="h2">
              <v-icon color="primary" icon="mdi-alert-circle-outline" />
              {{ t('dashboard.attentionTitle') }}
            </v-card-title>
            <v-card-text>
              <v-alert
                v-if="attentionItems.length === 0"
                icon="mdi-check-circle-outline"
                :text="t('dashboard.noWarningsDescription')"
                :title="t('dashboard.noWarningsTitle')"
                type="success"
                variant="tonal"
              />
              <v-list v-else lines="two">
                <v-list-item v-for="item in attentionItems" :key="item.title" :to="item.to">
                  <template #prepend>
                    <v-avatar :color="item.color" size="36" variant="tonal">
                      <v-icon :icon="item.icon" size="20" />
                    </v-avatar>
                  </template>
                  <v-list-item-title>{{ item.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item.detail }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <section class="mt-5" aria-labelledby="recent-activity-heading">
        <v-card variant="outlined">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon color="primary" icon="mdi-history" />
            <h2 id="recent-activity-heading" class="text-h6">{{ t('dashboard.recentActivity') }}</h2>
            <v-spacer />
            <v-btn size="small" to="/tasks" variant="text">{{ t('common.actions.viewAll') }}</v-btn>
          </v-card-title>
          <v-card-subtitle>{{ t('dashboard.recentSubtitle') }}</v-card-subtitle>
          <v-card-text>
            <div
              v-if="dashboard.tasks.recent.length === 0"
              class="text-center text-body-2 text-medium-emphasis py-8"
              data-testid="recent-activity-empty"
            >
              <v-icon class="d-block mx-auto mb-2" icon="mdi-inbox-outline" size="36" />
              {{ t('dashboard.noRecentActivity') }}
            </div>
            <v-list v-else class="pa-0" lines="two">
              <v-list-item
                v-for="task in dashboard.tasks.recent"
                :key="task.uuid"
                class="dashboard-task-row"
              >
                <template #prepend>
                  <v-avatar :color="getMethodColor(task.method)" size="38" variant="tonal">
                    <v-icon :icon="getResourceIcon(task.resource)" size="21" />
                  </v-avatar>
                </template>
                <v-list-item-title class="dashboard-task-title d-flex flex-wrap align-center ga-2">
                  <strong>{{ taskMethodLabel(task.method) }}</strong>
                  <span>{{ taskResourceLabel(task.resource) }}</span>
                  <span class="dashboard-task-object text-medium-emphasis text-truncate" :title="task.object">
                    {{ task.object }}
                  </span>
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatTimestamp(task.postTime) }}
                  <template v-if="task.userId"> · {{ task.userId }}</template>
                </v-list-item-subtitle>
                <template #append>
                  <v-chip :color="getStatusColor(task.status)" size="small" variant="tonal">
                    {{ taskStatusLabel(task.status) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </section>
    </template>
  </div>
</template>

<route lang="yaml">
meta:
  titleKey: navigation.dashboard
  layout: default
</route>

<script lang="ts" setup>
import {
  formatGib,
  formatNumber,
  formatPercentage,
  formatTimestamp,
  getDashboard,
  networkTypeLabel,
  nodeRoleLabel,
  progressPercent,
  ratioPercent,
  taskMethodLabel,
  taskResourceLabel,
  taskStatusLabel,
  utilizationColor,
} from '@/composables/dashboard'
import type { DashboardResponse } from '@/composables/dashboard'
import { useReloadListener } from '@/composables/trigger'
import { getMethodColor, getResourceIcon, getStatusColor } from '@/composables/task'
import { computed, onMounted, ref, shallowRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

type KpiItem = {
  title: string
  value: number
  detail: string
  icon: string
  to: string
}

type AllocationMetric = {
  label: string
  summary: string
  percent: number | null
  percentLabel: string
}

type AttentionItem = {
  title: string
  detail: string
  icon: string
  color: string
  to: string
}

const dashboard = shallowRef<DashboardResponse>()
const { t } = useI18n({ useScope: 'global' })
const isLoading = ref(true)
const loadError = ref(false)
let pendingRequest: Promise<void> | undefined
let refreshQueued = false

const isInitialLoading = computed(() => isLoading.value && !dashboard.value)
const isRefreshing = computed(() => isLoading.value && Boolean(dashboard.value))

const visibilityLabel = computed(() =>
  dashboard.value?.visibility === 'all'
    ? t('dashboard.visibilityAll')
    : t('dashboard.visibilityAssigned'),
)

const isInventoryEmpty = computed(() => {
  const value = dashboard.value
  if (!value) return false

  return value.nodes.count === 0 && value.vms.count === 0
    && value.storages.count === 0 && value.networks.count === 0 && value.images.count === 0
})

const kpis = computed<KpiItem[]>(() => {
  const value = dashboard.value
  if (!value) return []

  return [
    {
      title: t('dashboard.kpis.vms'),
      value: value.vms.count,
      detail: t('dashboard.kpis.running', { count: formatNumber(value.vms.statuses.running) }, value.vms.statuses.running),
      icon: 'mdi-desktop-tower',
      to: '/vms',
    },
    {
      title: t('dashboard.kpis.nodes'),
      value: value.nodes.count,
      detail: t('dashboard.kpis.cpuCores', { count: formatNumber(value.nodes.core) }, value.nodes.core),
      icon: 'mdi-server',
      to: '/nodes',
    },
    {
      title: t('dashboard.kpis.storagePools'),
      value: value.storages.count,
      detail: t('dashboard.valueAvailable', { value: formatGib(value.storages.availableGib) }),
      icon: 'mdi-database',
      to: '/storages',
    },
    {
      title: t('dashboard.kpis.networks'),
      value: value.networks.count,
      detail: t('dashboard.kpis.portGroups', { count: formatNumber(value.networks.portGroupCount) }, value.networks.portGroupCount),
      icon: 'mdi-wan',
      to: '/networks',
    },
    {
      title: t('dashboard.kpis.images'),
      value: value.images.count,
      detail: t('dashboard.kpis.inventoryImages'),
      icon: 'mdi-harddisk',
      to: '/images',
    },
    {
      title: t('dashboard.kpis.activeTasks'),
      value: value.tasks.incompleteCount,
      detail: t('dashboard.kpis.inProgress'),
      icon: 'mdi-progress-clock',
      to: '/tasks',
    },
  ]
})

const allocationMetrics = computed<AllocationMetric[]>(() => {
  const value = dashboard.value
  if (!value) return []

  const vcpuPercent = ratioPercent(value.vms.core, value.nodes.core)
  const memoryPercent = ratioPercent(value.vms.memoryGib, value.nodes.memoryGib)
  const storagePercent = ratioPercent(value.storages.usedGib, value.storages.capacityGib)

  return [
    {
      label: t('dashboard.metrics.vcpu'),
      summary: t('dashboard.metrics.ofCores', {
        value: formatNumber(value.vms.core),
        total: formatNumber(value.nodes.core),
      }),
      percent: vcpuPercent,
      percentLabel: vcpuPercent === null
        ? t('dashboard.capacityUnavailable')
        : t('dashboard.percentAllocated', { percent: formatPercentage(vcpuPercent) }),
    },
    {
      label: t('dashboard.metrics.memory'),
      summary: t('dashboard.metrics.ofValues', {
        value: formatGib(value.vms.memoryGib),
        total: formatGib(value.nodes.memoryGib),
      }),
      percent: memoryPercent,
      percentLabel: memoryPercent === null
        ? t('dashboard.capacityUnavailable')
        : t('dashboard.percentAllocated', { percent: formatPercentage(memoryPercent) }),
    },
    {
      label: t('dashboard.metrics.storage'),
      summary: t('dashboard.metrics.ofValues', {
        value: formatGib(value.storages.usedGib),
        total: formatGib(value.storages.capacityGib),
      }),
      percent: storagePercent,
      percentLabel: storagePercent === null
        ? t('dashboard.usageUnavailable')
        : t('dashboard.percentUsed', { percent: formatPercentage(storagePercent) }),
    },
  ]
})

const vmRunningPercent = computed(() => {
  const value = dashboard.value
  return value ? ratioPercent(value.vms.statuses.running, value.vms.count) : null
})

const vmStatuses = computed(() => {
  const statuses = dashboard.value?.vms.statuses
  if (!statuses) return []

  return [
    { label: t('dashboard.running'), count: statuses.running, color: 'primary', icon: 'mdi-play-circle-outline' },
    { label: t('dashboard.stopped'), count: statuses.stopped, color: 'grey', icon: 'mdi-stop-circle-outline' },
    { label: t('dashboard.maintenance'), count: statuses.maintenance, color: 'warning', icon: 'mdi-tools' },
    { label: t('dashboard.lostNode'), count: statuses.lostNode, color: 'error', icon: 'mdi-server-off' },
    { label: t('dashboard.deleted'), count: statuses.deleted, color: 'grey-darken-1', icon: 'mdi-delete-outline' },
    { label: t('dashboard.unknown'), count: statuses.unknown, color: 'warning', icon: 'mdi-help-circle-outline' },
  ]
})

const attentionItems = computed<AttentionItem[]>(() => {
  const value = dashboard.value
  if (!value) return []

  const items: AttentionItem[] = []
  if (value.tasks.failedLast24Hours > 0) {
    const count = value.tasks.failedLast24Hours
    items.push({
      title: t('dashboard.attention.failedTasks', { count: formatNumber(count) }, count),
      detail: t('dashboard.attention.failedTasksDetail'),
      icon: 'mdi-alert-octagon-outline',
      color: 'error',
      to: '/tasks',
    })
  }
  if (value.storages.highUsageCount > 0) {
    const count = value.storages.highUsageCount
    items.push({
      title: t('dashboard.attention.highStorage', { count: formatNumber(count) }, count),
      detail: t('dashboard.attention.highStorageDetail'),
      icon: 'mdi-database-alert-outline',
      color: 'error',
      to: '/storages',
    })
  }
  if (value.vms.statuses.lostNode > 0) {
    const count = value.vms.statuses.lostNode
    items.push({
      title: t('dashboard.attention.lostNode', { count: formatNumber(count) }, count),
      detail: t('dashboard.attention.lostNodeDetail'),
      icon: 'mdi-server-off',
      color: 'error',
      to: '/vms',
    })
  }
  if (value.vms.statuses.maintenance > 0) {
    const count = value.vms.statuses.maintenance
    items.push({
      title: t('dashboard.attention.maintenance', { count: formatNumber(count) }, count),
      detail: t('dashboard.attention.maintenanceDetail'),
      icon: 'mdi-tools',
      color: 'warning',
      to: '/vms',
    })
  }
  if (value.vms.statuses.deleted > 0) {
    const count = value.vms.statuses.deleted
    items.push({
      title: t('dashboard.attention.deleted', { count: formatNumber(count) }, count),
      detail: t('dashboard.attention.deletedDetail'),
      icon: 'mdi-delete-alert-outline',
      color: 'warning',
      to: '/vms',
    })
  }
  if (value.vms.statuses.unknown > 0) {
    const count = value.vms.statuses.unknown
    items.push({
      title: t('dashboard.attention.unknown', { count: formatNumber(count) }, count),
      detail: t('dashboard.attention.unknownDetail'),
      icon: 'mdi-help-circle-outline',
      color: 'warning',
      to: '/vms',
    })
  }
  return items
})

function loadDashboard(): Promise<void> {
  if (pendingRequest) {
    refreshQueued = true
    return pendingRequest
  }

  isLoading.value = true
  loadError.value = false
  const request = getDashboard(hasAdminScope(auth.scopes))
    .then((response) => {
      dashboard.value = response
    })
    .catch(() => {
      loadError.value = true
    })
    .finally(() => {
      if (pendingRequest === request) pendingRequest = undefined
      if (refreshQueued) {
        refreshQueued = false
        return loadDashboard()
      }
      isLoading.value = false
    })

  pendingRequest = request
  return request
}

useReloadListener(() => {
  void loadDashboard()
})

onMounted(() => {
  void loadDashboard()
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1800px;
  margin-inline: auto;
}

.dashboard-hero {
  position: relative;
  overflow: hidden;
  color: rgb(var(--v-theme-on-primary));
}

.dashboard-hero-subtitle {
  color: rgba(var(--v-theme-on-primary), 0.86);
}

.dashboard-hero-meta {
  color: rgba(var(--v-theme-on-primary), 0.9);
}

.dashboard-hero::after {
  position: absolute;
  inset: auto -70px -90px auto;
  width: 230px;
  height: 230px;
  content: "";
  background: rgba(var(--v-theme-on-primary), 0.08);
  border-radius: 50%;
  pointer-events: none;
}

.dashboard-hero-icon {
  width: 58px;
  height: 58px;
  background: rgba(var(--v-theme-on-primary), 0.14);
  border: 1px solid rgba(var(--v-theme-on-primary), 0.22);
  border-radius: 16px;
}

.dashboard-kpi-card {
  min-height: 126px;
}

.dashboard-kpi-icon {
  width: 52px;
  height: 52px;
  flex: 0 0 52px;
  background: rgba(var(--v-theme-primary), 0.1);
  border-radius: 14px;
}

.dashboard-kpi-value,
.dashboard-metric,
.dashboard-storage-row {
  font-variant-numeric: tabular-nums;
}

.dashboard-status-list {
  min-width: min(100%, 250px);
  background: transparent;
}

.dashboard-storage-row + .dashboard-storage-row,
.dashboard-task-row + .dashboard-task-row {
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.dashboard-inline-link {
  min-width: 0;
  max-width: min(100%, 24rem);
  height: auto;
  font-weight: 600;
}

.dashboard-inline-link :deep(.v-btn__content) {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-task-row :deep(.v-list-item__content),
.dashboard-task-title {
  min-width: 0;
}

.dashboard-task-object {
  flex: 1 1 12rem;
  min-width: 0;
  max-width: min(100%, 42rem);
}

.dashboard-message-width {
  max-width: 520px;
}

.min-width-0 {
  min-width: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 599px) {
  .dashboard-hero-icon {
    width: 48px;
    height: 48px;
  }

  .dashboard-task-row :deep(.v-list-item__append) {
    align-self: flex-start;
    margin-top: 8px;
  }
}
</style>
