<template>
  <div>
    <v-dialog width="800" v-model="model">
      <v-card>
        <v-form ref="dialogForm">
          <v-card-title>Administration Key</v-card-title>
          <v-card-text>
            This SSH key is used by Virty to operate each node. Passwordless sudo privileges are required.
            If you wish to restrict the user's permissions, please contact us via an issue.

            <v-switch v-model="requestData.generate" color="error" label="Generated on the server side" hide-details
              inset></v-switch>
            <v-textarea class="text-caption pt-3" outlined clearable auto-grow label="Key"
              v-model="requestData.privateKey" :disabled="requestData.generate"></v-textarea>
            <v-textarea class="text-caption" outlined clearable auto-grow label="Pub" v-model="requestData.publicKey"
              :disabled="requestData.generate"></v-textarea>

            <div class="text-error">
              <v-icon icon="mdi-alert-circle-outline"></v-icon>
              An SSH key already exists on the server.
              In this case, it will be overwritten and cannot be recovered, so please proceed with caution.
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn :loading="submitting" color="error" v-on:click="addNode" v-if="alreadyKeySave">Overwrite</v-btn>
            <v-btn :loading="submitting" color="primary" v-on:click="addNode" v-else>Submit</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { defineProps, defineModel } from 'vue'
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'

const { notify } = useNotification()

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
      notify({
        type: 'success',
        title: 'Add key successful',
        text: 'Wait until the task is completed'
      })
    } else {
      notify({
        type: 'error',
        title: 'Add key failed',
        text: 'Check the key format'
      })
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
