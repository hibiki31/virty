<template>
  <div v-if="auth.$state.tokenValidated && !auth.$state.authed">
    <setup-dialog></setup-dialog>
    <v-card class="mx-auto" max-width="400">
      <v-toolbar color="primary" dark>
        <v-toolbar-title>Login</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>
      <v-card-text>
        <v-text-field v-model="username" label="ID" prepend-icon="mdi-account" required type="text" variant="underlined"
          density="compact" @keydown.enter="login"></v-text-field>
        <v-text-field v-model="password" label="Password" prepend-icon="mdi-lock" required type="password"
          variant="underlined" density="compact" @keydown.enter="login"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn depressed color="primary" type="submit" :loading="isLoadingLogin" @click="login">Login</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<route lang="yaml">
meta:
  title: Virty - Login
  layout: login
</route>

<script lang="ts" setup>
import { useRouter, useRoute } from 'vue-router'
import { useNotification } from '@kyvg/vue3-notification'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/api'
import { getCookie, removeCookie, setCookie } from 'typescript-cookie'
import { onMounted, ref } from 'vue'

// module
const { notify } = useNotification()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const password = ref('')
const username = ref('')
const isLoadingLogin = ref(false)

const login = async () => {
  isLoadingLogin.value = true
  try {
    const res = await apiClient.POST('/api/auth', {
      body: {
        username: username.value,
        password: password.value,
        scope: ''
      },
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    })

    if (res.data) {
      setCookie('accessToken', res.data.access_token)
      auth.loginSuccess(res.data.access_token)
      await router.push((route.query.redirect as string | undefined) ?? '/')
      notify({
        type: 'success',
        title: 'Login successful',
        text: 'will be automatically redirected'
      })
    } else {
      notify({
        type: 'error',
        title: 'Login fail',
        text: typeof res.error?.detail === "string" ? res.error.detail : 'Unknown error',
      })
    }
  } catch {
    notify({
      type: 'error',
      title: 'Login fail',
      text: 'Unable to reach the authentication service',
    })
  } finally {
    isLoadingLogin.value = false
  }
}



const validateToken = async () => {
  const accessToken = getCookie('accessToken')

  if (!accessToken) {
    console.debug('token not found in cookie')
    auth.$state.tokenValidated = true
    return
  }

  auth.token = accessToken

  try {
    const res = await apiClient.GET('/api/auth/validate', {
      headers: {
        Authorization: 'Bearer ' + accessToken
      }
    })

    if (res.response.ok) {
      notify({
        type: 'success',
        title: 'Login successful',
        text: 'Token were valid',
      })
      auth.loginSuccess(accessToken)
      await router.push((route.query.redirect as string | undefined) ?? '/')
    } else {
      notify({
        type: 'error',
        title: 'Login Failed',
        text: 'Token have expired',
      })
      removeCookie('accessToken')
      auth.loginFailure()
    }
  } catch {
    notify({
      type: 'error',
      title: 'Login Failed',
      text: 'Unable to validate the saved token',
    })
    removeCookie('accessToken')
    auth.loginFailure()
  }
}

onMounted(async () => {
  await validateToken()
})
</script>
