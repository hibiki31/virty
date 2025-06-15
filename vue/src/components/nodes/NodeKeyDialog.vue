<template>
  <div>
    <v-dialog width="800" v-model="model">
      <v-card>
        <v-form ref="dialogForm">
          <v-card-title>Administration Key</v-card-title>
          <v-card-text>
            Using this SSH key, Virty manages nodes.
            <v-textarea class="text-caption pt-3" outlined clearable auto-grow label="Key"
              v-model="requestData.privateKey"></v-textarea>
            <v-textarea class="text-caption" outlined clearable auto-grow label="Pub"
              v-model="requestData.publicKey"></v-textarea>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn :loading="submitting" color="primary" v-on:click="addNode">Submit</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { defineProps, defineModel } from 'vue'
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'

const { notify } = useNotification()

const model = defineModel({ default: false })
const submitting = ref(false)

const requestData = reactive({
  privateKey: '',
  publicKey: ''
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

apiClient.GET('/api/nodes/key').then((res) => {
  requestData.publicKey = res.data?.publicKey || ''
  requestData.privateKey = res.data?.privateKey || ''
})


</script>

<style>
.v-textarea textarea {
  line-height: 1.1rem !important;
  font-family: monospace, serif;
}
</style>
