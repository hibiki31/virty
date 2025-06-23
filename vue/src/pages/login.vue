<template>
  <div>
    <setup-dialog></setup-dialog>
    <v-container class="fill-height" fluid v-if="auth.$state.tokenValidated && !auth.$state.authed">
      <v-row justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card>
            <v-toolbar color="primary" dark>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-text-field v-model="username" label="ID" prepend-icon="mdi-account" required type="text"
                variant="underlined" density="compact" @keydown.enter="login"></v-text-field>
              <v-text-field v-model="password" label="Password" prepend-icon="mdi-lock" required type="password"
                variant="underlined" density="compact" @keydown.enter="login"></v-text-field>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn depressed color="primary" type="submit" :loading="isLoadingLogin" @click="login">Login</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<route lang="yaml">
meta:
  title: Virty - Login
  layout: login
</route>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { asyncSleep } from '@/composables/sleep'
import { useNotification } from '@kyvg/vue3-notification'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/api'
import { getCookie, removeCookie, setCookie } from 'typescript-cookie'

// module
const { notify } = useNotification()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const password = ref('')
const username = ref('')
const isLoadingLogin = ref(false)

const loadingLogin = async () => {
  await asyncSleep(300)
  isLoadingLogin.value = false
}

const login = async () => {
  isLoadingLogin.value = true
  apiClient.POST('/api/auth', {
    body: {
      username: username.value,
      password: password.value,
      scope: ''
    },
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then((res) => {
    if (res.data) {
      setCookie('accessToken', res.data.access_token)
      auth.loginSuccess(res.data.access_token)
      router.push((route.query.redirect as string | undefined) ?? '/')
      notify({
        type: 'success',
        title: 'Login successful',
        text: 'will be automatically redirected'
      })
    } else {
      notify({
        type: 'error',
        title: 'Login fail',
        text: typeof res.error.detail === "string" ? res.error.detail : 'known error',
      })
    }
  }).finally(() => {
    isLoadingLogin.value = false
  })
}



const validateToken = () => {
  const accessToken = getCookie('accessToken')

  if (!accessToken) {
    console.debug('token not found in cookie')
    auth.$state.tokenValidated = true
    return
  }

  auth.token = accessToken

  apiClient.GET('/api/auth/validate', {
    headers: {
      Authorization: 'Bearer ' + accessToken
    }
  }).then((res) => {
    if (res.response.ok) {
      notify({
        type: 'success',
        title: 'Login successful',
        text: 'Token were valid',
      })
      auth.loginSuccess(accessToken)
      router.push((route.query.redirect as string | undefined) ?? '/')
    } else {
      notify({
        type: 'error',
        title: 'Login Failed',
        text: 'Token have expired',
      })
      removeCookie('accessToken')
      auth.$state.tokenValidated = true
    }
  })
}

onMounted(async () => {
  validateToken()
})
</script>
