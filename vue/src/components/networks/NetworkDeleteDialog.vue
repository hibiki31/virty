<template>
  <v-dialog v-model="model" persistent max-width="290">
    <v-card>
      <v-card-title class="headline">
        {{ t('dialogs.networkDelete.title') }}
      </v-card-title>
      <v-card-text>{{ props.item?.name }}</v-card-text>
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
import type { typeListNetwork } from '@/composables/network';
import { apiClient } from '@/api';
import { asyncSleep } from '@/composables/sleep';
import notify, { apiErrorRef } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import { useI18n } from 'vue-i18n';
const router = useRouter()

const { t } = useI18n({ useScope: 'global' })
const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<typeListNetwork["data"][0]>,
    required: false,
  }
})

const loading = ref(false)


async function submit() {
  if (props.item) {
    loading.value = true
    try {
      const res = await apiClient.DELETE('/api/tasks/networks/{uuid}', { params: { path: { uuid: props.item.uuid } } })

      if (res.response.ok) {
        notify('success', translationRef('dialogs.networkDelete.success'), translationRef('dialogs.networkDelete.wait'))
        model.value = false
        await asyncSleep(600)
        await router.push("/networks")
      } else {
        notify('error', translationRef('dialogs.networkDelete.failed'), apiErrorRef(res.error))
      }
    } catch {
      notify('error', translationRef('dialogs.networkDelete.failed'), translationRef('dialogs.networkDelete.unreachable'))
    } finally {
      loading.value = false
    }
  }
}
</script>
