<template>
  <v-dialog v-model="dialogState" max-width="640">
    <v-form @submit.prevent="submit">
      <v-card>
        <v-card-title>Create Project</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="name"
            data-testid="project-name"
            label="Name"
            maxlength="64"
            :rules="[r.required, r.limitLength64]"
          />
          <v-autocomplete
            v-model="memberIds"
            data-testid="project-members"
            :items="users"
            :loading="usersLoading"
            item-title="username"
            item-value="username"
            label="Members"
            multiple
            chips
            closable-chips
            :rules="[membersRequired]"
          />
          <v-alert density="compact" type="info" variant="tonal">
            The signed-in administrator is included explicitly so the Project remains manageable in this UI.
            All members must sign in again before the new Project appears in their token.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogState = false">Cancel</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import { createProject } from '@/composables/project'
import { getUserList, type UserList } from '@/composables/user'
import notify, { notifyTask } from '@/composables/notify'
import r from '@/composables/rules'
import { useAuthStore } from '@/stores/auth'

const dialogState = defineModel({ default: false })
const emit = defineEmits<{ created: [] }>()
const auth = useAuthStore()
const name = ref('')
const memberIds = ref<string[]>([])
const users = ref<UserList['data']>([])
const usersLoading = ref(false)
const loading = ref(false)

function membersRequired(value: string[]): true | string {
  if (value.length === 0) return 'Select at least one member.'
  if (auth.username && !value.includes(auth.username)) {
    return 'Keep the signed-in administrator as a member.'
  }
  return true
}

async function loadUsers() {
  usersLoading.value = true
  try {
    const response = await getUserList({ limit: 0, page: 1, nameLike: '' })
    users.value = response.data
  } finally {
    usersLoading.value = false
  }
}

async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) return

  loading.value = true
  try {
    const tasks = await createProject({ name: name.value.trim(), memberIds: memberIds.value })
    notifyTask(tasks[0]?.uuid)
    dialogState.value = false
    emit('created')
  } catch (error) {
    notify('error', 'Create Project failed', error instanceof Error ? error.message : undefined)
  } finally {
    loading.value = false
  }
}

watch(dialogState, open => {
  if (!open) return
  name.value = ''
  memberIds.value = auth.username ? [auth.username] : []
  void loadUsers()
})
</script>
