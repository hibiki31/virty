<template>
  <v-card>
    <v-card-actions>
      <v-btn id="user-create-button" color="primary" variant="flat" prepend-icon="mdi-account-plus" data-testid="user-create"
        @click="open('create', undefined, $event)">{{ t('userManagement.create') }}</v-btn>
      <v-spacer></v-spacer>
      <v-text-field v-model="query.nameLike" density="compact" :label="t('pages.users.filters.search')" prepend-inner-icon="mdi-magnify"
        variant="solo-filled" flat hide-details single-line @update:model-value="reload"></v-text-field>
    </v-card-actions>
    <v-data-table-server v-model:items-per-page="itemsPerPage" :headers="headers" :items="items.data"
      v-model:page="pageState" density="comfortable" :items-length="items.count" :loading="loading" item-value="username"
      @update:options="loadItems">
      <template v-slot:item.scopes="{ item }">
        {{ displayScopes(item.scopes) }}
      </template>
      <template #item.publickeys="{ item }">
        {{ (item.publickeys ?? []).map(key => key.name).join(', ') || '—' }}
      </template>
      <template #item.actions="{ item }">
        <div class="user-actions">
          <v-btn size="small" variant="text" :data-testid="`user-edit-${item.username}`"
            @click="open('edit', item.username, $event)">{{ t('userManagement.edit') }}</v-btn>
          <v-btn size="small" variant="text" :disabled="item.username === auth.username"
            :title="item.username === auth.username ? t('userManagement.selfReset') : undefined"
            @click="open('reset', item.username, $event)">{{ t('userManagement.reset') }}</v-btn>
          <v-btn size="small" variant="text" color="error" :disabled="item.username === auth.username"
            :title="item.username === auth.username ? t('userManagement.selfDelete') : undefined"
            :data-testid="`user-delete-${item.username}`"
            @click="open('delete', item.username, $event)">{{ t('userManagement.delete') }}</v-btn>
        </div>
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

    <v-alert v-if="error" type="error" variant="tonal" role="alert">{{ formatApiError(error) }}</v-alert>
    <UserDialog v-model="dialog" :action="action" :target="target" @saved="saved" @closed="restoreFocus" />
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
import UserDialog from '@/components/users/UserDialog.vue'
import type { UserAction } from '@/composables/user'
import { useAuthStore } from '@/stores/auth'
import { formatApiError } from '@/composables/apiError'

const { t } = useI18n({ useScope: 'global' })

const loading = ref(false)
const auth = useAuthStore()
const error = ref<unknown>(null)
const dialog = ref(false)
const action = ref<UserAction>('create')
const target = ref<string>()
let activator: HTMLElement | null = null
let deleted = false
function open(next: UserAction, username: string | undefined, event: Event) {
  activator = event.currentTarget as HTMLElement
  deleted = false
  action.value = next
  target.value = username
  dialog.value = true
}
function restoreFocus() {
  const element = !deleted && activator?.isConnected ? activator : document.getElementById('user-create-button')
  element?.focus()
}
async function saved() {
  deleted = action.value === 'delete'
  await reload()
}
const itemsPerPage = ref(20)
const pageState = ref(1)

const headers = computed(() => [
  { title: t('pages.users.columns.name'), value: 'username' },
  { title: t('pages.users.columns.projects'), value: 'projects' },
  { title: t('pages.users.columns.scopes'), value: 'scopes' },
  { title: t('pages.users.columns.publicKeys'), value: 'publickeys' },
  { title: t('userManagement.actions'), value: 'actions', sortable: false },
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
  error.value = null

  try {
    items.value = await getUserList(query.value)
    if (items.value.count > 0 && items.value.data.length === 0 && pageState.value > 1) {
      pageState.value = Math.max(1, Math.ceil(items.value.count / itemsPerPage.value))
    }
  } catch (reason) {
    error.value = reason
  } finally {
    loading.value = false
  }
}

useReloadListener(async () => {
  await reload()
})

</script>

<style scoped>
.user-actions { display: flex; flex-wrap: wrap; gap: 4px; }
</style>
