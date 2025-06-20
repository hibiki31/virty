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

import { useRouter } from 'vue-router'
import { useStateStore } from '@/stores/state'
import { useAuthStore } from '@/stores/auth'

import { defineEmits, ref, onMounted } from 'vue'
import { apiClient } from '@/api'
import notify from '@/composables/notify'

const router = useRouter()
const state = useStateStore()
const auth = useAuthStore()

// emit
const emit = defineEmits(['getVideo'])
const taskChecking = ref(false)
const taskCount = ref(0)
const taskHash = ref('')
const enableAutoReload = ref(true)

const logout = async () => {
  removeAuth()
  notify('success', 'You have been logged out', 'You will be redirected to the login page.')

  await asyncSleep(200)
  location.reload()
}

const taskCheck = async () => {
  // 複数実行されてる場合は終了
  if (taskChecking.value) {
    return
  }
  taskChecking.value = true;

  while (true) {
    // 未認証の場合は待ち
    if (!auth.authed) {
      await asyncSleep(1000)
      continue;
    }
    const res = await apiClient.GET('/api/tasks/incomplete', {
      params: {
        query: {
          hash: taskHash.value,
          admin: true
        }
      }
    })
    if (res.data) {
      taskHash.value = res.data.hash

      // リロードをトリガーする条件
      if ((taskCount.value > res.data.count) && enableAutoReload.value) {
        notify("info", "Realod", "Reloading due to task completion")
        setTimeout(() => (state.trigger()), 100)
      }
      taskCount.value = res.data.count
    }
  }
}

onMounted(() => {
  taskCheck()
})

</script>
