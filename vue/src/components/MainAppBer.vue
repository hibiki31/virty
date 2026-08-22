<template>
  <v-app-bar color="primary" prominent density="compact">
    <v-app-bar-nav-icon variant="text" @click.stop="state.showSideDrawer = !state.showSideDrawer"></v-app-bar-nav-icon>
    <v-toolbar-title>Virty</v-toolbar-title>

    <v-spacer></v-spacer>

    <v-switch v-model="enableAutoReload" hide-details color="error" class="pa-6" hint="Enable auto relaod"></v-switch>

    <v-progress-circular indeterminate color="error" v-if="taskCount > 0" size="24"></v-progress-circular>
    <v-progress-circular color="error" v-else size="24"></v-progress-circular>

    <v-btn variant="text" icon="mdi-logout-variant" class="" @click="logout"></v-btn>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { removeAuth } from '@/composables/auth'
import { asyncSleep } from '@/composables/sleep'
import { applyTaskPollingSnapshot, createTaskPoller } from '@/composables/taskPolling'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { useStateStore } from '@/stores/state'
import { useAuthStore } from '@/stores/auth'

import { apiClient } from '@/api'
import notify from '@/composables/notify'

const state = useStateStore()
const auth = useAuthStore()

const taskCount = ref(0)
const enableAutoReload = ref(true)

const logout = async () => {
  removeAuth()
  auth.loginFailure()
  notify('success', 'You have been logged out', 'You will be redirected to the login page.')

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
      notifyReload: () => notify("info", "Reload", "Reloading due to task completion"),
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
