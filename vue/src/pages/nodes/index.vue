<template>
  <v-card>
    <node-add-dialog v-model="dialogAdd"></node-add-dialog>
    <node-key-dialog v-model="dialogKey"></node-key-dialog>
    <v-card-actions>
      <v-btn prepend-icon="mdi-file-key" variant="flat" color="primary" size="small"
        @click="dialogKey = true">KEY</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="dialogAdd = true">JOIN</v-btn>
      <v-btn prepend-icon="mdi-server-remove" variant="flat" color="error" size="small">LEAVE</v-btn>
    </v-card-actions>
    <v-data-table :items="items.data" :loading="loading" :headers="headers" :items-per-page="10" density="comfortable">
      <template v-slot:item.name="{ item }">
        <router-link :to="'/nodes/' + item.name" class="font-mono">{{ item.name }}</router-link>
      </template>
    </v-data-table>
  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Nodes
</route>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { apiClient } from '@/api'
import type { paths } from '@/api/openapi'

const dialogAdd = ref(false)
const dialogKey = ref(false)

const loading = ref(false)

const headers = [
  { title: 'Status', value: 'status' },
  { title: 'Name', value: 'name' },
  { title: 'IP', value: 'domain' },
  { title: 'Port', value: 'port' },
  { title: 'Core', value: 'core' },
  { title: 'Memory', value: 'memory' },
  { title: 'CPU', value: 'cpuGen' },
  { title: 'OS', value: 'osName' },
  { title: 'QEMU', value: 'qemuVersion' },
  { title: 'Libvirt', value: 'libvirtVersion' },
  { title: 'Roles', value: 'roles' },
  { title: 'Actions', value: 'actions' }
]

const items = ref<paths['/api/nodes']['get']['responses']['200']['content']['application/json']>({
  count: 0,
  data: [],
})

const load = () => {
  apiClient.GET('/api/nodes', {
    params: {
      query: {
        admin: true,
        limit: 100,
      }
    }
  }).then((res) => {
    if (res.data) {
      items.value = res.data
    }
  })
}

onMounted(() => {
  load()
})

</script>
