<template>
  <v-dialog width="400" v-model="model">
    <v-card>
      <v-form ref="nodeAddForm">
        <v-card-title>Register node</v-card-title>
        <v-card-text>
          <v-text-field v-model="postData.name" label="Name"
            :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
            counter="64"></v-text-field>
          <v-text-field v-model="postData.userName" label="User" :rules="[required]"></v-text-field>
          <v-text-field v-model="postData.domain" label="IP or Doain" :rules="[required]"></v-text-field>
          <v-text-field v-model="postData.port" label="Port" :rules="[$required, $intValueRestrictions]"
            counter="64"></v-text-field>
          <v-text-field v-model="postData.description" label="Descriptions" counter="128"></v-text-field>
          <v-checkbox v-model="postData.libvirtRole" label='Provisioning as kvm host'></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="addNode">Register</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>


import { reactive, ref } from 'vue';
import { defineProps, defineModel } from 'vue'
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'

const { notify } = useNotification()

const model = defineModel({ default: false })

const postData = reactive({
  name: '',
  userName: '',
  domain: '',
  port: 0,
  description: '',
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
