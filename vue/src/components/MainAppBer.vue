<template>
  <v-app-bar color="primary" prominent density="compact">
    <v-app-bar-nav-icon variant="text" @click.stop="state.showSideDrawer = !state.showSideDrawer"></v-app-bar-nav-icon>
    <v-toolbar-title>Virty</v-toolbar-title>

    <v-spacer></v-spacer>
    <v-btn variant="text" icon="mdi-logout-variant" class="ml-5" @click="logout"></v-btn>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { removeAuth } from '@/composables/auth'
import { asyncSleep } from '@/composables/sleep'

import { useRouter } from 'vue-router'
import { useNotification } from '@kyvg/vue3-notification'
import { useStateStore } from '@/stores/state'

import { defineEmits } from 'vue'

const router = useRouter()
const { notify } = useNotification()
const state = useStateStore()

// emit
const emit = defineEmits(['getVideo'])


const logout = async () => {
  removeAuth()
  notify({
    type: 'success',
    title: 'ログアウトしました',
    text: 'ログインページに遷移します',
  })

  await asyncSleep(200)
  location.reload()
}
</script>
