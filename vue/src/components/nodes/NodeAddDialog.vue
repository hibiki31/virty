<template>
  <v-dialog width="400" v-model="model">
    <v-card :title="t('dialogs.nodeAdd.title')">
      <v-form @submit.prevent="addNode">
        <v-card-text>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.name" :label="t('common.fields.name')"
            :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
            counter="64"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.userName" :label="t('common.fields.user')"
            :rules="[r.required]"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.domain" :label="t('dialogs.nodeAdd.domain')"
            :rules="[r.required]"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.port" :label="t('common.fields.port')"
            :rules="[r.required, r.portTCP]"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.description" :label="t('common.fields.description')"
            counter="128"></v-text-field>
          <v-checkbox color="primary" density="comfortable" v-model="postData.libvirtRole"
            :label="t('dialogs.nodeAdd.kvmHost')"></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="model = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">{{ t('common.actions.register') }}</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { apiClient } from '@/api';
import type { components } from '@/api/openapi';
import { reactive, ref } from 'vue';
import { useLocalizedRules } from '@/composables/rules';
import notify, { apiErrorRef } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()

const model = defineModel({ default: false })
const loading = ref(false)

const postData = reactive<components['schemas']['NodeForCreate']>({
  name: '',
  userName: '',
  domain: '',
  port: 22,
  // APIへ送る運用データの既定値として原文を維持する。
  description: 'KVM Node',
  libvirtRole: true
})


const addNode = async (event: Promise<{ valid: boolean }>) => {
  if (!(await event).valid) return

  loading.value = true
  try {
    const res = await apiClient.POST('/api/tasks/nodes', { body: postData })
    if (res.response.ok) {
      notify('success', translationRef('dialogs.nodeAdd.success'), translationRef('dialogs.nodeAdd.wait'))
      model.value = false
    } else {
      notify('error', translationRef('dialogs.nodeAdd.failed'), apiErrorRef(res.error))
    }
  } catch {
    notify('error', translationRef('dialogs.nodeAdd.failed'), translationRef('dialogs.nodeAdd.unreachable'))
  } finally {
    loading.value = false
  }
}


</script>
