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
import notify from '@/composables/notify'
import r from '@/composables/rules'
import { apiClient } from '@/api'
import { asyncSleep } from '@/composables/sleep';
import { onMounted, ref } from 'vue';

const dialogState = ref(false)
const postData = ref({
  username: '',
  password: ''
})

const loading = ref(false)


async function commit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  loading.value = true
  try {
    const res = await apiClient.POST("/api/auth/setup", { body: postData.value })

    if (res.response.ok) {
      notify("success", "Setup successful")
      await asyncSleep(500)
      await reload()
    } else if (res.error) {
      notify("error", "Failed Setup", res.error)
    }
  } catch {
    notify("error", "Failed Setup", "Unable to reach the setup service")
  } finally {
    loading.value = false
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
