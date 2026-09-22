<template>
  <fieldset class="key-editor" :disabled="disabled">
    <legend class="text-subtitle-1">{{ t('userManagement.keys') }}</legend>
    <p v-if="!keys.length" class="text-body-2">{{ t('userManagement.noKeys') }}</p>
    <div v-for="(key, index) in keys" :key="index" class="key-row">
      <v-text-field v-model="key.name" :label="t('userManagement.keyName')" :rules="[nameRule]"
        maxlength="255" :data-testid="`key-name-${index}`" />
      <v-textarea v-model="key.publickey" :label="t('userManagement.keyValue')" :rules="[keyRule]"
        rows="2" auto-grow :data-testid="`key-value-${index}`" />
      <v-btn variant="text" color="error" icon="mdi-delete-outline" :disabled="disabled"
        :aria-label="t('userManagement.removeKey', { index: index + 1 })"
        :title="t('userManagement.removeKey', { index: index + 1 })"
        @click="keys = keys.filter((_, i) => i !== index)" />
    </div>
    <v-btn variant="tonal" color="primary" prepend-icon="mdi-plus" :disabled="disabled || keys.length >= 64"
      data-testid="add-public-key" @click="keys = [...keys, { name: '', publickey: '' }]">
      {{ t('userManagement.addKey') }}
    </v-btn>
  </fieldset>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { PublicKey } from '@/composables/user'

defineProps<{ disabled?: boolean }>()
const keys = defineModel<PublicKey[]>({ required: true })
const { t } = useI18n({ useScope: 'global' })
const nameRule = (value: string) => !value.trim() ? t('validation.required')
  : keys.value.filter(key => key.name === value).length === 1 || t('userManagement.keyNamesUnique')
const keyRule = (value: string) => Boolean(value.trim()) && !value.includes('PRIVATE KEY')
  && /^(ssh-|ecdsa-)[^\s]+ [A-Za-z0-9+/]+={0,3}(?:[ \t].*)?$/.test(value.trim())
  || t('fieldErrors.invalid_public_key')
</script>

<style scoped>
.key-editor { border: 0; padding: 0; min-width: 0; display: grid; gap: 12px; }
.key-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; align-items: start; }
.key-row > :first-child { grid-column: 1 / -1; }
</style>
