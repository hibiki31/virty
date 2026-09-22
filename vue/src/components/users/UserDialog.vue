<template>
  <v-dialog :model-value="model" max-width="640" :persistent="busy" :aria-label="t(`userManagement.${action}`)"
    @update:model-value="close" @after-leave="emit('closed')">
    <v-card :title="t(`userManagement.${action}`)">
      <v-form @submit.prevent="submit">
        <v-card-text class="user-form">
          <v-progress-linear v-if="loading" indeterminate :aria-label="t(`userManagement.${action}`)" />
          <v-alert v-if="error" type="error" variant="tonal" role="alert" data-testid="user-error">{{ formatApiError(error) }}</v-alert>
          <v-btn v-if="!ready && !loading" variant="tonal" @click="load">{{ t('userManagement.retry') }}</v-btn>
          <template v-if="ready">
            <v-text-field v-model="username" :label="t('userManagement.name')" :readonly="action !== 'create'"
              :disabled="busy" :rules="[nameRule]" maxlength="255" data-testid="user-name" />
            <template v-if="action === 'create' || action === 'edit'">
              <v-autocomplete v-model="scopes" :items="scopeOptions" :item-title="userScopeLabel"
                :label="t('userManagement.scopes')" multiple chips closable-chips :disabled="busy"
                data-testid="user-scopes" />
              <v-alert type="info" variant="tonal" density="compact">{{ t('userManagement.permissionsNotice') }}</v-alert>
              <PublicKeyEditor v-model="publickeys" :disabled="busy" />
            </template>
            <template v-if="action === 'create' || action === 'reset'">
              <NewPasswordFields v-model="password" v-model:confirmation="confirmation" :disabled="busy" />
              <v-alert v-if="action === 'reset'" type="info" variant="tonal">{{ t('userManagement.sessionNotice') }}</v-alert>
            </template>
            <template v-if="action === 'delete'">
              <p>{{ t('userManagement.deleteConfirm', { name: username }) }}</p>
              <v-checkbox v-model="confirmed" :label="t('userManagement.deleteCheck')" :rules="[checkedRule]"
                :disabled="busy" data-testid="user-delete-confirm" />
            </template>
          </template>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" :disabled="busy" @click="close">{{ t('userManagement.cancel') }}</v-btn>
          <v-btn type="submit" variant="flat" :color="action === 'delete' ? 'error' : 'primary'"
            :disabled="!ready || loading" :loading="busy" data-testid="user-submit">
            {{ t(action === 'create' || action === 'delete' || action === 'reset' ? `userManagement.${action}` : 'userManagement.save') }}
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { createUser, getUser, getUserScopes, updateUser, deleteUser, resetUserPassword,
  type UserAction, type PublicKey } from '@/composables/user'
import { userScopeLabel, translationRef } from '@/composables/i18n'
import { formatApiError } from '@/composables/apiError'
import { useUnsavedChanges } from '@/composables/unsavedChanges'
import { removeAuth } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'
import notify from '@/composables/notify'
import PublicKeyEditor from './PublicKeyEditor.vue'
import NewPasswordFields from './NewPasswordFields.vue'

const props = defineProps<{ action: UserAction; target?: string }>()
const model = defineModel<boolean>({ required: true })
const emit = defineEmits<{ saved: []; closed: [] }>()
const { t } = useI18n({ useScope: 'global' })
const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const scopes = ref<string[]>(['user'])
const availableScopes = ref<string[]>([])
const publickeys = ref<PublicKey[]>([])
const password = ref('')
const confirmation = ref('')
const confirmed = ref(false)
const busy = ref(false)
const loading = ref(false)
const ready = ref(false)
const error = ref<unknown>(null)
const initial = ref('')
const initialScopes = ref('')
const snapshot = computed(() => JSON.stringify([username.value, scopes.value, publickeys.value, password.value, confirmation.value]))
const dirty = computed(() => model.value && ready.value && snapshot.value !== initial.value)
const { confirmDiscard } = useUnsavedChanges(dirty, busy)
const scopeOptions = computed(() => [...new Set([...availableScopes.value, ...scopes.value])])
const nameRule = (value: string) => Boolean(value.trim()) && value.length <= 255 && !/[\/\x00-\x1f]/.test(value)
  || t('userManagement.nameInvalid')
const checkedRule = (value: boolean) => value || t('userManagement.deleteCheck')
let loadVersion = 0

async function load() {
  const version = ++loadVersion
  loading.value = true
  ready.value = false
  error.value = null
  password.value = ''
  confirmation.value = ''
  confirmed.value = false
  try {
    const [user, options] = await Promise.all([
      props.action === 'create' ? Promise.resolve(null) : getUser(props.target!),
      props.action === 'create' || props.action === 'edit' ? getUserScopes() : Promise.resolve([]),
    ])
    if (version !== loadVersion || !model.value) return
    username.value = user?.username ?? ''
    scopes.value = user?.scopes?.map(scope => scope.name) ?? ['user']
    publickeys.value = user?.publickeys?.map(key => ({ ...key })) ?? []
    availableScopes.value = options
    initial.value = snapshot.value
    initialScopes.value = JSON.stringify(scopes.value)
    ready.value = true
  } catch (reason) {
    if (version === loadVersion) error.value = reason
  } finally {
    if (version === loadVersion) loading.value = false
  }
}

function close() {
  if (!confirmDiscard()) return
  ++loadVersion
  password.value = ''
  confirmation.value = ''
  model.value = false
}

async function submit(event: Promise<{ valid: boolean }>) {
  const validation = await event
  if (busy.value || !ready.value || !validation.valid) return
  busy.value = true
  error.value = null
  try {
    const body = { scopes: scopes.value.map(name => ({ name })), publickeys: publickeys.value }
    if (props.action === 'create') await createUser({ ...body, username: username.value, password: password.value })
    else if (props.action === 'edit') await updateUser(username.value, body)
    else if (props.action === 'delete') await deleteUser(username.value)
    else await resetUserPassword(username.value, password.value)
    initial.value = snapshot.value
    model.value = false
    password.value = ''
    confirmation.value = ''
    notify('success', translationRef(props.action === 'delete' ? 'userManagement.deleted' : 'userManagement.saved'))
    emit('saved')
    if (props.action === 'edit' && username.value === auth.username
      && JSON.stringify(scopes.value) !== initialScopes.value) {
      removeAuth()
      auth.loginFailure()
      busy.value = false
      await router.replace('/login')
    }
  } catch (reason) {
    error.value = reason
  } finally {
    busy.value = false
  }
}

watch(model, open => { if (open) void load() })
</script>

<style scoped>
.user-form { display: grid; gap: 16px; }
</style>
