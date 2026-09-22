<template>
  <v-navigation-drawer v-model="state.showSideDrawer">
    <v-list density="compact" nav class="primary--text text--primary">
      <v-list-item prepend-icon="mdi-view-dashboard" :title="$t('navigation.dashboard')" :to="{ name: '/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-desktop-tower" :title="$t('navigation.vms')" :to="{ name: '/vms/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-server" :title="$t('navigation.nodes')" :to="{ name: '/nodes/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-database" :title="$t('navigation.storages')" :to="{ name: '/storages/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-harddisk" :title="$t('navigation.images')" :to="{ name: '/images/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-wan" :title="$t('navigation.networks')" :to="{ name: '/networks/' }"></v-list-item>
      <v-list-item v-if="canReadProjects" prepend-icon="mdi-folder-account-outline" :title="$t('navigation.projects')"
        :to="{ name: '/projects/' }"></v-list-item>
      <v-list-item v-if="isAdmin" prepend-icon="mdi-account" :title="$t('navigation.users')"
        :to="{ name: '/users/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-account-cog" :title="$t('userManagement.account')"
        to="/account"></v-list-item>
      <v-list-item v-if="isAdmin" prepend-icon="mdi-robot-outline" :title="$t('navigation.agent')"
        :to="{ name: '/agent/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-checkbox-multiple-marked-outline" :title="$t('navigation.tasks')"
        :to="{ name: '/tasks/' }"></v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list class="primary--text text--primary" nav>
      <v-chip class="ma-2" label size="x-small">
        <v-icon icon="mdi-monitor" start></v-icon>
        {{ breakPoint.toUpperCase() }}
      </v-chip>
    </v-list>
    <v-divider></v-divider>
    <v-list class="primary--text text--primary" nav>
      <a class="d-inline-block mx-2 social-link" :aria-label="$t('navigation.api')" :href="apiURL" rel="noopener noreferrer" target="_blank">
        <v-icon icon="mdi-api" size="30" />
      </a>
      <a class="d-inline-block mx-2 social-link" :aria-label="$t('navigation.documentation')" href="https://hibiki31.github.io/virty/" rel="noopener noreferrer"
        target="_blank">
        <v-icon icon="mdi-book-multiple" size="24" />
      </a>
    </v-list>
    <v-divider></v-divider>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { useStateStore } from '@/stores/state'
import { useAuthStore } from '@/stores/auth'
import { hasScope } from '@/composables/auth'
const apiURL = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL + "/api" : "/api"
const state = useStateStore()
const auth = useAuthStore()
const isAdmin = computed(() => auth.scopes.includes('admin'))
const canReadProjects = computed(() => hasScope(auth.scopes, 'project.read'))
import { useDisplay } from 'vuetify'

function useBreakpoint() {
  const display = useDisplay()
  return computed(() => display.name.value as 'xs' | 'sm' | 'md' | 'lg' | 'xl')
}

const breakPoint = useBreakpoint()
</script>

<style scoped lang="sass">
  .social-link :deep(.v-icon)
    color: rgba(var(--v-theme-on-background), var(--v-disabled-opacity))
    text-decoration: none
    transition: .2s ease-in-out

    &:hover
      color: rgba(var(--v-theme-primary))
</style>
