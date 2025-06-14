<template>
  <v-navigation-drawer v-model="store.showSideDrawer">
    <v-list density="compact" nav class="primary--text text--primary">
      <v-list-item prepend-icon="mdi-cube-outline" title="VM" :to="{ name: '/' }"></v-list-item>
      <v-list-item prepend-icon="mdi-server" title="Node" :to="{ name: '/list/node' }"></v-list-item>
      <v-list-item prepend-icon="mdi-checkbox-multiple-marked-outline" title="Task"
        :to="{ name: '/tasks' }"></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { useStateStore } from '@/stores/state'

const store = useStateStore()

</script>
