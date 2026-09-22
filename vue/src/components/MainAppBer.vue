<template>
  <v-app-bar color="primary" prominent density="compact">
    <v-app-bar-nav-icon variant="text" :aria-label="t('appBar.toggleNavigation')"
      @click.stop="state.showSideDrawer = !state.showSideDrawer"></v-app-bar-nav-icon>
    <v-toolbar-title class="d-none d-sm-flex">Virty</v-toolbar-title>

    <v-spacer></v-spacer>

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
  </v-app-bar>
</template>

<script lang="ts" setup>
import { removeAuth } from '@/composables/auth'
import { asyncSleep } from '@/composables/sleep'
import { applyTaskPollingSnapshot, createTaskPoller } from '@/composables/taskPolling'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import LocaleSwitcher from '@/components/LocaleSwitcher.vue'
import { useStateStore } from '@/stores/state'
import { useAuthStore } from '@/stores/auth'

import { apiClient } from '@/api'
import notify from '@/composables/notify'
import { translationRef } from '@/composables/i18n'

const state = useStateStore()
const auth = useAuthStore()
const { t } = useI18n({ useScope: 'global' })

const taskCount = ref(0)
const enableAutoReload = ref(true)

const logout = async () => {
  if (!window.dispatchEvent(new Event('virty:before-logout', { cancelable: true }))) return
  removeAuth()
  auth.loginFailure()
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
          admin: true
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
