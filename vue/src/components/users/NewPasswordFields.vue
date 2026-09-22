<template>
  <v-text-field v-model="password" type="password" autocomplete="new-password"
    :label="t('userManagement.newPassword')" :rules="[passwordRule]" :disabled="disabled"
    :hint="t('userManagement.passwordPolicy')" persistent-hint data-testid="new-password" />
  <v-text-field v-model="confirmation" type="password" autocomplete="new-password"
    :label="t('userManagement.confirmPassword')" :rules="[confirmationRule]" :disabled="disabled"
    data-testid="confirm-password" />
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { validNewPassword } from '@/composables/user'
defineProps<{ disabled?: boolean }>()
const password = defineModel<string>({ required: true })
const confirmation = defineModel<string>('confirmation', { required: true })
const { t } = useI18n({ useScope: 'global' })
const passwordRule = (value: string) => validNewPassword(value) || t('userManagement.passwordPolicy')
const confirmationRule = (value: string) => Boolean(value) && value === password.value || t('userManagement.passwordMismatch')
</script>
