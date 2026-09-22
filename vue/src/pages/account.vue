<template>
  <div class="account-settings">
    <v-alert v-if="loadError" type="error" variant="tonal" role="alert">
      {{ formatApiError(loadError) }}
      <v-btn variant="text" @click="load">{{ t('userManagement.retry') }}</v-btn>
    </v-alert>
    <v-progress-linear v-if="loading" indeterminate />
    <template v-if="profile">
      <v-card :title="t('userManagement.account')">
        <v-card-text class="account-form">
          <div><strong>{{ t('userManagement.name') }}</strong>: {{ profile.username }}</div>
          <div><strong>{{ t('userManagement.scopes') }}</strong>: {{ userScopeListLabel(profile.scopes ?? []) }}</div>
          <div>
            <strong>{{ t('userManagement.projects') }}</strong>
            <div class="project-list">
              <v-chip v-for="project in profile.projects" :key="project.id" :to="`/projects/${project.id}`" size="small">
                {{ formatProjectName(project) }}
              </v-chip>
              <span v-if="!profile.projects?.length">{{ t('userManagement.noProjects') }}</span>
            </div>
          </div>
        </v-card-text>
      </v-card>
      <v-card>
        <v-form @submit.prevent="saveKeys">
          <v-card-text class="account-form">
            <v-alert v-if="keysError" type="error" variant="tonal" role="alert" data-testid="account-keys-error">{{ formatApiError(keysError) }}</v-alert>
            <PublicKeyEditor v-model="keys" :disabled="busy" />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" variant="flat" type="submit" :loading="keysSaving" :disabled="busy || !keysDirty"
              data-testid="account-save-keys">{{ t('userManagement.save') }}</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
      <v-card :title="t('userManagement.changePassword')">
        <v-form @submit.prevent="savePassword">
          <v-card-text class="account-form">
            <v-alert v-if="passwordError" type="error" variant="tonal" role="alert" data-testid="account-password-error">{{ formatApiError(passwordError) }}</v-alert>
            <v-text-field v-model="currentPassword" type="password" autocomplete="current-password"
              :label="t('userManagement.currentPassword')" :rules="[required]" :disabled="busy"
              data-testid="current-password" />
            <NewPasswordFields v-model="password" v-model:confirmation="confirmation" :disabled="busy" />
            <v-alert type="info" variant="tonal">{{ t('userManagement.sessionNotice') }}</v-alert>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" variant="flat" type="submit" :loading="passwordSaving" :disabled="busy"
              data-testid="account-change-password">{{ t('userManagement.changePassword') }}</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </template>
  </div>
</template>

<route lang="yaml">
meta:
  titleKey: userManagement.account
</route>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { getMyProfile, updateMyPublickeys, changeMyPassword, type PublicKey, type UserProfile } from '@/composables/user'
import { useUnsavedChanges } from '@/composables/unsavedChanges'
import { formatApiError } from '@/composables/apiError'
import { formatProjectName } from '@/composables/project'
import { translationRef, userScopeListLabel } from '@/composables/i18n'
import { removeAuth } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import notify from '@/composables/notify'
import PublicKeyEditor from '@/components/users/PublicKeyEditor.vue'
import NewPasswordFields from '@/components/users/NewPasswordFields.vue'

const { t } = useI18n({ useScope: 'global' })
const router = useRouter()
const auth = useAuthStore()
const profile = ref<UserProfile>()
const keys = ref<PublicKey[]>([])
const originalKeys = ref('[]')
const currentPassword = ref('')
const password = ref('')
const confirmation = ref('')
const loading = ref(false)
const keysSaving = ref(false)
const passwordSaving = ref(false)
const busy = computed(() => keysSaving.value || passwordSaving.value)
const loadError = ref<unknown>(null)
const keysError = ref<unknown>(null)
const passwordError = ref<unknown>(null)
const keysDirty = computed(() => JSON.stringify(keys.value) !== originalKeys.value)
const dirty = computed(() => keysDirty.value || Boolean(currentPassword.value || password.value || confirmation.value))
useUnsavedChanges(dirty, busy)
const required = (value: string) => Boolean(value) || t('validation.required')

async function load() {
  loading.value = true
  loadError.value = null
  try {
    profile.value = await getMyProfile()
    keys.value = (profile.value.publickeys ?? []).map(key => ({ ...key }))
    originalKeys.value = JSON.stringify(keys.value)
  } catch (error) {
    loadError.value = error
  } finally {
    loading.value = false
  }
}

async function saveKeys(event: Promise<{ valid: boolean }>) {
  const validation = await event
  if (busy.value || !validation.valid) return
  keysSaving.value = true
  keysError.value = null
  try {
    profile.value = await updateMyPublickeys(keys.value)
    keys.value = (profile.value.publickeys ?? []).map(key => ({ ...key }))
    originalKeys.value = JSON.stringify(keys.value)
    notify('success', translationRef('userManagement.saved'))
  } catch (error) {
    keysError.value = error
  } finally {
    keysSaving.value = false
  }
}

async function savePassword(event: Promise<{ valid: boolean }>) {
  const validation = await event
  if (busy.value || !validation.valid) return
  if (keysDirty.value && !window.confirm(t('userManagement.discard'))) return
  passwordSaving.value = true
  passwordError.value = null
  try {
    await changeMyPassword(currentPassword.value, password.value)
    currentPassword.value = password.value = confirmation.value = ''
    originalKeys.value = JSON.stringify(keys.value)
    removeAuth()
    auth.loginFailure()
    useAppStore().$reset()
    notify('success', translationRef('userManagement.passwordChanged'))
    passwordSaving.value = false
    await router.replace('/login')
  } catch (error) {
    passwordError.value = error
  } finally {
    passwordSaving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.account-settings { max-width: 48rem; display: grid; gap: 24px; }
.account-form { display: grid; gap: 16px; overflow-wrap: anywhere; }
.project-list { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
</style>
