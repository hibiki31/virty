<template>
  <v-app-bar color="primary" prominent density="compact"
    :extension-height="auth.canUseAdminMode && route.meta.projectFilter && xs ? 104 : 56">
    <v-app-bar-nav-icon variant="text" :aria-label="t('appBar.toggleNavigation')"
      @click.stop="state.showSideDrawer = !state.showSideDrawer"></v-app-bar-nav-icon>
    <v-toolbar-title class="d-none d-sm-flex">Virty</v-toolbar-title>

    <v-spacer></v-spacer>

    <v-switch v-if="auth.canUseAdminMode && lgAndUp" :model-value="selectedAdminMode"
      :label="t(auth.adminMode ? 'appBar.adminMode' : 'appBar.generalMode')"
      :aria-label="t('appBar.switchAdminMode')" data-testid="admin-mode-switch"
      class="d-none d-lg-flex flex-grow-0 mx-3" color="warning" hide-details
      @update:model-value="changeMode" />

    <ProjectFilterSelect
      v-if="route.meta.projectFilter && !xs"
      :model-value="projectId"
      class="app-bar-project mr-4"
      @update:model-value="updateProjectFilter"
    />

    <LocaleSwitcher class="d-none d-md-flex mr-2" />
    <LocaleSwitcher compact class="d-flex d-md-none" />

    <v-switch v-model="enableAutoReload" :aria-label="t('appBar.autoReload')" hide-details color="error"
      class="d-none d-md-flex mx-2" :hint="t('appBar.autoReload')"></v-switch>
    <v-btn v-if="enableAutoReload" class="d-flex d-md-none" color="error" icon="mdi-refresh-auto"
      :aria-label="t('appBar.autoReload')" variant="text" @click="enableAutoReload = false"></v-btn>
    <v-btn v-else class="d-flex d-md-none" icon="mdi-refresh-off" :aria-label="t('appBar.autoReload')"
      variant="text" @click="enableAutoReload = true"></v-btn>

    <v-progress-circular :aria-label="t('appBar.taskCount', { count: taskCount }, taskCount)" indeterminate color="error"
      v-if="taskCount > 0" size="24"></v-progress-circular>
    <v-progress-circular :aria-label="t('appBar.taskCount', { count: 0 }, 0)" color="error" v-else
      size="24"></v-progress-circular>

    <v-btn variant="text" icon="mdi-logout-variant" :aria-label="t('appBar.logout')" @click="logout"></v-btn>
    <template v-if="(auth.canUseAdminMode && !lgAndUp) || (route.meta.projectFilter && xs)" #extension>
      <div class="app-bar-project-row d-flex flex-wrap align-center ga-2 px-4 pb-2">
        <v-switch v-if="auth.canUseAdminMode && !lgAndUp" :model-value="selectedAdminMode"
          :label="t(auth.adminMode ? 'appBar.adminMode' : 'appBar.generalMode')"
          :aria-label="t('appBar.switchAdminMode')" data-testid="admin-mode-switch"
          class="flex-grow-0" color="warning" hide-details @update:model-value="changeMode" />
        <ProjectFilterSelect v-if="route.meta.projectFilter && xs" class="app-bar-project-mobile"
          :model-value="projectId" @update:model-value="updateProjectFilter" />
      </div>
    </template>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { hasAdminScope, removeAuth } from '@/composables/auth'
import { asyncSleep } from '@/composables/sleep'
import { applyTaskPollingSnapshot, createTaskPoller } from '@/composables/taskPolling'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useDisplay } from 'vuetify'

import LocaleSwitcher from '@/components/LocaleSwitcher.vue'
import ProjectFilterSelect from '@/components/projects/ProjectFilterSelect.vue'
import { useProjectFilter } from '@/composables/projectFilter'
import { useAppStore } from '@/stores/app'
import { useStateStore } from '@/stores/state'
import { useAuthStore } from '@/stores/auth'

import { apiClient } from '@/api'
import notify from '@/composables/notify'
import { translationRef } from '@/composables/i18n'

const state = useStateStore()
const auth = useAuthStore()
const app = useAppStore()
const route = useRoute()
const { xs, lgAndUp } = useDisplay()
const { projectId, updateProjectFilter } = useProjectFilter()
const { t } = useI18n({ useScope: 'global' })

watch(() => route.fullPath, () => {
  if (route.meta.projectFilter) app.projectId = projectId.value
}, { immediate: true })

const taskCount = ref(0)
const enableAutoReload = ref(true)
const selectedAdminMode = ref(auth.adminMode)

async function changeMode(enabled: boolean | null) {
  selectedAdminMode.value = enabled === true
  if (!window.dispatchEvent(new Event('virty:before-mode-change', { cancelable: true }))) {
    // 取消時はnative checkboxの表示も元に戻す。
    await nextTick()
    selectedAdminMode.value = auth.adminMode
    return
  }
  auth.setAdminMode(enabled === true)
  window.location.assign(import.meta.env.BASE_URL)
}

const logout = async () => {
  if (!window.dispatchEvent(new Event('virty:before-logout', { cancelable: true }))) return
  removeAuth()
  auth.loginFailure()
  app.$reset()
  notify('success', translationRef('appBar.logoutComplete'), translationRef('appBar.logoutRedirect'))

  await asyncSleep(200)
  location.reload()
}

const taskPoller = createTaskPoller({
  isAuthenticated: () => auth.authed,
  async request(referenceHash, signal) {
    const res = await apiClient.GET('/api/tasks/incomplete', {
      params: {
        query: {
          referenceHash,
          admin: hasAdminScope(auth.scopes)
        }
      },
      signal,
    })

    if (!res.data) {
      throw new Error('incomplete taskの取得に失敗しました')
    }

    return res.data
  },
  onSnapshot(snapshot, previousCount) {
    applyTaskPollingSnapshot(snapshot, previousCount, enableAutoReload.value, {
      notifyReload: () => notify("info", translationRef('appBar.reload'), translationRef('appBar.reloadAfterTask')),
      setTaskCount: (count) => {
        taskCount.value = count
      },
      setTaskUuids: (uuids) => {
        state.task_uuids = uuids
      },
      triggerReload: () => state.trigger(),
    })
  },
})

onMounted(() => {
  taskPoller.start()
})

onBeforeUnmount(() => {
  taskPoller.stop()
})

</script>

<style scoped>
.app-bar-project {
  flex: 0 1 20rem;
  min-width: 0;
}

.app-bar-project-row {
  width: 100%;
}

.app-bar-project-mobile {
  flex: 1 1 100%;
  min-width: 0;
}

</style>
