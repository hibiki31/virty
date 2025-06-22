<template>
  <v-navigation-drawer v-model="store.showSideDrawer">
    <v-list density="compact" nav class="primary--text text--primary">
      <v-list-item prepend-icon="mdi-cube-outline" title="VM" :to="{ name: '/vms/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-server" title="Node" :to="{ name: '/nodes/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-database" title="Storage" :to="{ name: '/storages/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-harddisk" title="Image" :to="{ name: '/images/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-wan" title="Network" :to="{ name: '/networks/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-checkbox-multiple-marked-outline" title="Task"
        :to="{ name: '/tasks/' }"></v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list class="primary--text text--primary" nav>
      <a class="d-inline-block mx-2 social-link" :href="apiURL" rel="noopener noreferrer" target="_blank">
        <v-icon icon="mdi-api" size="30" />
      </a>
      <a class="d-inline-block mx-2 social-link" href="https://hibiki31.github.io/virty/" rel="noopener noreferrer"
        target="_blank">
        <v-icon icon="mdi-book-multiple" size="24" />
      </a>
      <a class="d-inline-block mx-2 social-link" @click="copyToken" rel="noopener noreferrer">
        <v-icon icon="mdi-code-json" size="24" />
      </a>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { useStateStore } from '@/stores/state'
import { useAuthStore } from '@/stores/auth'
import notify from '@/composables/notify'

const apiURL = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL + "/api" : "/api"
const store = useStateStore()
const auth = useAuthStore()

async function copyToken() {
  await navigator.clipboard.writeText(auth.token)
  notify("success", "Copied the JWT token", "Use it from a Python script")
}

</script>

<style scoped lang="sass">
  .social-link :deep(.v-icon)
    color: rgba(var(--v-theme-on-background), var(--v-disabled-opacity))
    text-decoration: none
    transition: .2s ease-in-out

    &:hover
      color: rgba(var(--v-theme-primary))
</style>
