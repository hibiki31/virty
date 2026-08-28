<template>
  <v-dialog v-model="model" max-width="400">
    <v-card>
      <v-form ref="formRef" @submit.prevent="submit">
        <v-card-title class="headline">
          {{ t('dialogs.imageDelete.title') }}
        </v-card-title>
        <v-card-text>
          {{ t('dialogs.imageDelete.confirm') }}
          <v-checkbox density="comfortable" :label="t('dialogs.imageDelete.confirmation', { count: props.item?.length || 0 }, props.item?.length || 0)"
            :rules="[r.requiredCheckbox]" color="error"></v-checkbox>
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
    type: Object as PropType<schemas['Image'][]>,
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
    console.log(props.item)
    for (const v of props.item) {
      console.log(v)
      const res = await apiClient.DELETE('/api/tasks/storages/{uuid}/images/{name}', {
        params: { path: { uuid: v.storageUuid, name: v.name } }
      })
      if (res.data) {
        notifyTask(res.data[0].uuid)
        model.value = false
      }
      if (res.error) {
        notify('error', translationRef('dialogs.imageDelete.failed'), apiErrorRef(res.error))
      }
    }
    apiClient.PUT('/api/tasks/images').then((res) => {
      if (res.data) {
        notifyTask(res.data[0]?.uuid)
      }
    })

    await asyncSleep(800)
    loading.value = false
  }
}
</script>
