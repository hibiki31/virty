<template>
  <div>
    <v-dialog width="800" v-model="model">
      <v-card>
        <v-form ref="dialogForm">
          <v-card-title>{{ t('dialogs.nodeKey.title') }}</v-card-title>
          <v-card-text>
            {{ t('dialogs.nodeKey.description') }}

            <v-switch v-model="requestData.generate" color="error" :label="t('dialogs.nodeKey.generated')" hide-details
              inset></v-switch>
            <v-textarea class="text-caption pt-3" outlined clearable auto-grow :label="t('dialogs.nodeKey.privateKey')"
              v-model="requestData.privateKey" :disabled="requestData.generate"></v-textarea>
            <v-textarea class="text-caption" outlined clearable auto-grow :label="t('dialogs.nodeKey.publicKey')" v-model="requestData.publicKey"
              :disabled="requestData.generate"></v-textarea>

            <div class="text-error">
              <v-icon icon="mdi-alert-circle-outline"></v-icon>
              {{ t('dialogs.nodeKey.warning') }}
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn :loading="submitting" color="error" v-on:click="addNode" v-if="alreadyKeySave">{{ t('common.actions.overwrite') }}</v-btn>
            <v-btn :loading="submitting" color="primary" v-on:click="addNode" v-else>{{ t('common.actions.submit') }}</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { apiClient } from '@/api';
import { useI18n } from 'vue-i18n'
import notify, { apiErrorRef } from '@/composables/notify'
import { translationRef } from '@/composables/i18n'

const { t } = useI18n({ useScope: 'global' })

const model = defineModel({ default: false })
const submitting = ref(false)
const alreadyKeySave = ref(false)

const requestData = reactive({
  privateKey: '',
  publicKey: '',
  generate: false,
})

const addNode = () => {
  apiClient.POST('/api/nodes/key', { body: requestData }).then((res) => {
    if (res.response.ok) {
      model.value = false
      notify('success', translationRef('dialogs.nodeKey.success'), translationRef('dialogs.nodeKey.wait'))
    } else {
      notify('error', translationRef('dialogs.nodeKey.failed'), apiErrorRef(res.error))
    }
    submitting.value = false
  })
}

function reload() {
  apiClient.GET('/api/nodes/key').then((res) => {
    requestData.publicKey = res.data?.publicKey || ''
    alreadyKeySave.value = (res.data?.publicKey !== undefined)
  })
}

watch(model, (newVal) => {
  if (newVal) {
    reload()
  }
})

</script>

<style>
.v-textarea textarea {
  line-height: 1.1rem !important;
  font-family: monospace, serif;
}
</style>
