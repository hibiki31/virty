<template>
  <v-dialog width="400" v-model="model">
    <v-card title="Register Node">
      <v-card-text>
        <v-form>
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
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="addNode">Register</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import * as r from '@/composables/rules';
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'

const { notify } = useNotification()

const model = defineModel({ default: false })

const postData = reactive({
  name: '',
  userName: '',
  domain: '',
  port: 22,
  description: 'KVM Node',
  libvirtRole: true
})


const addNode = () => {
  apiClient.POST('/api/tasks/nodes', { body: postData }).then((res) => {
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
        text: res.error.detail
      })
    }
  })
}


</script>
