<template>
  <v-dialog width="400" v-model="dialogState" persistent>
    <v-card>
      <v-container>
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
          <v-btn color="primary" v-on:click="commit">Setup</v-btn>
        </v-card-actions>
      </v-container>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { asyncSleep } from '@/composables/sleep'
import notify from '@/composables/notify'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/api'
import { getCookie, removeCookie, setCookie } from 'typescript-cookie'
import * as r from '@/composables/rules';

const showPassword = ref(false)
const dialogState = ref(false)
const postData = ref({
  username: '',
  password: ''
})

async function commit() {
  apiClient.POST("/api/auth/setup", { body: postData.value }).then((res) => {
    if (res.response.ok) {
      notify("success", "Setup successful")
    } else {
      notify("error", "known value")
    }
  })
}

async function reload() {
  apiClient.GET("/api/version").then((res) => {
    if (res.data) {
      dialogState.value = res.data.initialized
    }
  })
}

onMounted(async () => {
  await reload()
})

</script>
