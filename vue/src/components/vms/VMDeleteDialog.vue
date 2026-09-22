<template>
  <v-dialog v-model="model" persistent max-width="290">
    <v-card>
      <v-card-title class="headline">
        {{ t('dialogs.vmDelete.title') }}
      </v-card-title>
      <v-card-text>{{ t('dialogs.vmDelete.description') }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="success" text @click="model = false">
          {{ t('common.actions.cancel') }}
        </v-btn>
        <v-btn :loading="loading" color="error" text @click="submit()">
          {{ t('common.actions.delete') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { schemas } from '@/composables/schemas';
import { apiClient } from '@/api';
import notify, { apiErrorRef } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import { asyncSleep } from '@/composables/sleep';
import { useI18n } from 'vue-i18n';
const router = useRouter()
const { t } = useI18n({ useScope: 'global' })

const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['DomainDetail']>,
    required: false,
  }
})

const loading = ref(false)


async function submit() {
  if (props.item) {
    loading.value = true
    try {
      const res = await apiClient.DELETE('/api/tasks/vms/{uuid}', { params: { path: { uuid: props.item.uuid } } })

      if (res.response.ok) {
        notify('success', translationRef('dialogs.vmDelete.success'), translationRef('dialogs.vmDelete.wait'))
        model.value = false
        await asyncSleep(600)
        await router.push("/vms")
      } else if (res.error) {
        notify('error', translationRef('dialogs.vmDelete.failed'), apiErrorRef(res.error))
      }
    } catch {
      notify('error', translationRef('dialogs.vmDelete.failed'), translationRef('dialogs.vmDelete.unreachable'))
    } finally {
      loading.value = false
    }
  }
}
</script>
