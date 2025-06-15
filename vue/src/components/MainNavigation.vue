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
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { useStateStore } from '@/stores/state'

const store = useStateStore()

</script>
