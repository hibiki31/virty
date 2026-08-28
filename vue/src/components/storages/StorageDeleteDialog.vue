<template>
  <v-dialog v-model="model" max-width="400">
    <v-card>
      <v-form ref="formRef" @submit.prevent="submit">
        <v-card-title class="headline">
          {{ t('dialogs.storageDelete.title') }}
        </v-card-title>
        <v-card-text>
          {{ t('dialogs.storageDelete.confirm') }}
          <v-checkbox density="comfortable" :label="t('dialogs.storageDelete.confirmation', { name: props.item?.name || '' })" :rules="[r.requiredCheckbox]"
            color="error"></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="success" text @click="model = false">
            {{ t('common.actions.cancel') }}
          </v-btn>
          <v-btn :loading="loading" color="error" text type="submit">
            {{ t('common.actions.delete') }}
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { schemas } from '@/composables/schemas';
import { apiClient } from '@/api';
import notify, { apiErrorRef, notifyTask } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import { asyncSleep } from '@/composables/sleep';
import { useI18n } from 'vue-i18n';
import { useLocalizedRules } from '@/composables/rules';

const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()

const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['Storage']>,
    required: false,
  }
})

const loading = ref(false)


async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  if (props.item) {
    loading.value = true
    const res = await apiClient.DELETE('/api/tasks/storages/{uuid}', { params: { path: { uuid: props.item.uuid } } })
    await asyncSleep(800)

    if (res.data) {
      notifyTask(res.data[0].uuid)
      model.value = false
    }
    if (res.error) {
      notify('error', translationRef('dialogs.storageDelete.failed'), apiErrorRef(res.error))
    }
    loading.value = false
  }
}
</script>
