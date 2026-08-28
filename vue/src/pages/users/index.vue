<template>
  <v-card>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" :label="t('pages.users.filters.search')" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="name"
      @update:options="loadItems">
      <template v-slot:item.scopes="{ item }">
        {{ displayScopes(item.scopes) }}
      </template>
      <template #item.projects="{ item }">
        <v-chip
          v-for="project in item.projects"
          :key="project.id"
          class="ma-1"
          size="x-small"
          :to="`/projects/${project.id}`"
        >{{ formatProjectName(project) }}</v-chip>
      </template>
    </v-data-table-server>

  </v-card>
</template>

<route lang="yaml">
meta:
  titleKey: pages.users.documentTitle
  requiresAdmin: true
</route>

<script lang="ts" setup>
import { ref } from 'vue'
import { getUserList, initUserList, type UserListQuery } from '@/composables/user'
import { userScopeListLabel } from '@/composables/i18n'
import { useI18n } from 'vue-i18n'
import { formatProjectName } from '@/composables/project'

const { t } = useI18n({ useScope: 'global' })

const loading = ref(false)
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = computed(() => [
  { title: t('pages.users.columns.name'), value: 'username' },
  { title: t('pages.users.columns.projects'), value: 'projects' },
  { title: t('pages.users.columns.scopes'), value: 'scopes' },
  { title: t('pages.users.columns.publicKeys'), value: 'publickeys' },
])

const query = ref<UserListQuery>({
  limit: 20,
  page: 1,
  nameLike: "",
})

const items = ref(initUserList)

function displayScopes(scopes: Array<{ name: string }> | undefined): string {
  return userScopeListLabel((scopes ?? []).map(scope => scope.name))
}

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
