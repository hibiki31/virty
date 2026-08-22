<template>
  <v-dialog width="400" v-model="model">
    <v-card title="Register Node">
      <v-form @submit.prevent="addNode">
        <v-card-text>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.name" label="Name"
            :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
            counter="64"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.userName" label="User"
            :rules="[r.required]"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.domain" label="IP or Doain"
            :rules="[r.required]"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.port" label="Port"
            :rules="[r.required, r.portTCP]"></v-text-field>
          <v-text-field variant="outlined" density="comfortable" v-model="postData.description" label="Descriptions"
            counter="128"></v-text-field>
          <v-checkbox color="primary" density="comfortable" v-model="postData.libvirtRole"
            label='Provisioning as kvm host'></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="model = false">Cancel</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">Register</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'
import type { components } from '@/api/openapi';
import { reactive, ref } from 'vue';
import r from '@/composables/rules';

const { notify } = useNotification()

const model = defineModel({ default: false })
const loading = ref(false)

const postData = reactive<components['schemas']['NodeForCreate']>({
  name: '',
  userName: '',
  domain: '',
  port: 22,
  description: 'KVM Node',
  libvirtRole: true
})


const addNode = async (event: Promise<{ valid: boolean }>) => {
  if (!(await event).valid) return

  loading.value = true
  try {
    const res = await apiClient.POST('/api/tasks/nodes', { body: postData })
    if (res.response.ok) {
      notify({
        type: 'success',
        title: 'Join Node successful',
        text: 'Wait until the task is completed'
      })
      model.value = false
    } else {
      notify({
        type: 'error',
        title: 'Join Node failed',
        text: typeof res.error?.detail === 'string' ? res.error.detail : 'Unknown error'
      })
    }
  } catch {
    notify({
      type: 'error',
      title: 'Join Node failed',
      text: 'Unable to reach the node service'
    })
  } finally {
    loading.value = false
  }
}


</script>
