<template>
  <v-dialog v-model="dialogState" max-width="640">
    <v-form @submit.prevent="submit">
      <v-card>
        <v-card-title>{{ t('dialogs.projectCreate.title') }}</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="name"
            data-testid="project-name"
            :label="t('common.fields.name')"
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
            :label="t('dialogs.projectCreate.members')"
            multiple
            chips
            closable-chips
            :rules="[membersRequiredRule]"
          />
          <v-alert density="compact" type="info" variant="tonal">
            {{ t('dialogs.projectCreate.membershipNotice') }}
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogState = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn data-testid="project-create-submit" color="primary" type="submit" :loading="loading">{{ t('common.actions.create') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { createProject } from '@/composables/project'
import { getUserList, type UserList } from '@/composables/user'
import notify, { notificationContentFromError, notifyTask } from '@/composables/notify'
import { translationRef } from '@/composables/i18n'
import { localizeRule, useLocalizedRules } from '@/composables/rules'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const dialogState = defineModel({ default: false })
const emit = defineEmits<{ created: [] }>()
const auth = useAuthStore()
const { locale, t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()
const name = ref('')
const memberIds = ref<string[]>([])
const users = ref<UserList['data']>([])
const usersLoading = ref(false)
const loading = ref(false)

function membersRequired(value: string[]) {
  if (value.length === 0) {
    return translationRef('dialogs.projectCreate.validation.memberRequired')
  }
  if (auth.username && !value.includes(auth.username)) {
    return translationRef('dialogs.projectCreate.validation.keepAdministrator')
  }
  return true
}

const membersRequiredRule = computed(() => {
  void locale.value
  return localizeRule(membersRequired)
})

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
    notify(
      'error',
      translationRef('dialogs.projectCreate.failed'),
      notificationContentFromError(error),
    )
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
