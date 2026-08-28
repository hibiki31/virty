<template>
  <v-dialog v-model="dialogState" persistent width="400">
    <v-card>
      <v-form ref="formRef" @submit.prevent="commit">
        <v-card-title class="d-flex align-center">
          <span data-testid="setup-title">{{ t('setup.title') }}</span>
          <v-spacer />
          <LocaleSwitcher test-id="setup-locale-switcher" />
        </v-card-title>
        <v-card-text>
          {{ t('setup.createAdmin') }}
          <v-text-field v-model="postData.username" variant="underlined" density="compact" :label="t('setup.adminUsername')"
            class="pt-3" :rules="[r.required, r.limitLength32, r.characterRestrictions, r.firstCharacterRestrictions]"
            counter="64"></v-text-field>
          <v-text-field v-model="postData.password" variant="underlined" density="compact" :rules="[r.required]"
            type="password" :label="t('common.fields.password')" :hint="t('setup.passwordHint')" counter></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" type="submit" :loading="loading">{{ t('common.actions.setup') }}</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import notify, { apiErrorRef } from '@/composables/notify'
import { translationRef } from '@/composables/i18n'
import { useLocalizedRules } from '@/composables/rules'
import { apiClient } from '@/api'
import { asyncSleep } from '@/composables/sleep';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import LocaleSwitcher from '@/components/LocaleSwitcher.vue';

const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()

const dialogState = ref(false)
const postData = ref({
  username: '',
  password: ''
})

const loading = ref(false)


async function commit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  loading.value = true
  try {
    const res = await apiClient.POST("/api/auth/setup", { body: postData.value })

    if (res.response.ok) {
      notify("success", translationRef('setup.success'))
      await asyncSleep(500)
      await reload()
    } else if (res.error) {
      notify("error", translationRef('setup.failed'), apiErrorRef(res.error))
    }
  } catch {
    notify("error", translationRef('setup.failed'), translationRef('setup.unreachable'))
  } finally {
    loading.value = false
  }
}

async function reload() {
  apiClient.GET("/api/version").then((res) => {
    if (res.data) {
      dialogState.value = !res.data.initialized
    }
  })
}

onMounted(async () => {
  await reload()
})

</script>
