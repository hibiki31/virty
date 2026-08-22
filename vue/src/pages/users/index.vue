<template>
  <v-card>
    <v-card-actions>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary" size="small"
        @click="stateCreateDialog = true">CREATE</v-btn>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - VMs
</route>

<script lang="ts" setup>
import { ref } from 'vue'
import { getUserList, initUserList, type UserListQuery } from '@/composables/user'

const loading = ref(false)
const stateCreateDialog = ref(false)
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = [
  { title: 'Name', value: 'username' },
  { title: 'Projects', value: 'projects' },
  { title: 'scopes', value: 'scopes' },
  { title: 'publickeys', value: 'publickeys' },
]

const query = ref<UserListQuery>({
  admin: true,
  limit: 20,
  page: 1,
  nameLike: "",
})

const items = ref(initUserList)

async function loadItems({ page = 1, itemsPerPage = 10 }) {
  query.value.page = page
  query.value.limit = itemsPerPage

  await reload()
}

async function reload() {
  loading.value = true

  try {
    items.value = await getUserList(query.value)
  } finally {
    loading.value = false
  }
}

useReloadListener(async () => {
  await reload()
})

</script>
