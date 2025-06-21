<template>
  <v-dialog width="400" v-model="dialogState" persistent>
    <v-card>
      <v-form ref="formRef" @submit.prevent="commit">
        <v-card-title>Setup Virty</v-card-title>
        <v-card-text>
          Create an administrative user.
          <v-text-field v-model="postData.username" variant="underlined" density="compact" label="Admin username"
            class="pt-3" :rules="[r.required, r.limitLength32, r.characterRestrictions, r.firstCharacterRestrictions]"
            counter="64"></v-text-field>
          <v-text-field v-model="postData.password" variant="underlined" density="compact" :rules="[r.required]"
            type="password" label="Password" hint="At least 1 characters" counter></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" type="submit" :loading="loading">Setup</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import notify from '@/composables/notify'
import { apiClient } from '@/api'
import { asyncSleep } from '@/composables/sleep';

import * as r from '@/composables/rules';

const dialogState = ref(false)
const postData = ref({
  username: '',
  password: ''
})

const loading = ref(false)


async function commit(event: Promise<{ valid: boolean }>) {
  loading.value = true

  if (!(await event).valid) {
    return
  }

  const res = await apiClient.POST("/api/auth/setup", { body: postData.value })
  await asyncSleep(1000)

  loading.value = false

  if (res.response.ok) {
    notify("success", "Setup successful")
    await asyncSleep(500)
    await reload()
  } else if (res.error) {
    notify("error", "Failed Setup", res.error)
  }


}

async function reload() {
  apiClient.GET("/api/version").then((res) => {
    if (res.data) {
      dialogState.value = !res.data.initialized
    }
  })
}

onMounted(async () => {
  await reload()
})

</script>
