<template>
  <div v-if="auth.$state.tokenValidated && !auth.$state.authed">
    <setup-dialog></setup-dialog>
    <v-card class="mx-auto" max-width="400">
      <v-toolbar color="primary" dark>
        <v-toolbar-title>{{ t('pages.login.heading') }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <locale-switcher />
      </v-toolbar>
      <v-card-text>
        <v-text-field v-model="username" data-testid="login-username" :label="t('pages.login.username')" prepend-icon="mdi-account" required type="text" variant="underlined"
          density="compact" @keydown.enter="login"></v-text-field>
        <v-text-field v-model="password" data-testid="login-password" :label="t('pages.login.password')" prepend-icon="mdi-lock" required type="password"
          variant="underlined" density="compact" @keydown.enter="login"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn depressed color="primary" data-testid="login-submit" type="submit" :loading="isLoadingLogin" @click="login">{{ t('pages.login.submit') }}</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<route lang="yaml">
meta:
  titleKey: pages.login.documentTitle
  layout: login
</route>

<script lang="ts" setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/api'
import { getCookie, removeCookie, setCookie } from 'typescript-cookie'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'
import notify, { apiErrorRef } from '@/composables/notify'
import { translationRef } from '@/composables/i18n'

// module
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { t } = useI18n({ useScope: 'global' })

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
      notify('success', translationRef('pages.login.notifications.successTitle'), translationRef('pages.login.notifications.redirecting'))
    } else {
      notify('error', translationRef('pages.login.notifications.failureTitle'), apiErrorRef(res.error))
    }
  } catch {
    notify('error', translationRef('pages.login.notifications.failureTitle'), translationRef('pages.login.notifications.serviceUnavailable'))
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
      notify('success', translationRef('pages.login.notifications.successTitle'), translationRef('pages.login.notifications.tokenValid'))
      auth.loginSuccess(accessToken, true)
      await router.push((route.query.redirect as string | undefined) ?? '/')
    } else {
      notify('error', translationRef('pages.login.notifications.failureTitle'), apiErrorRef(res.error))
      removeCookie('accessToken')
      auth.loginFailure()
    }
  } catch {
    notify('error', translationRef('pages.login.notifications.failureTitle'), translationRef('pages.login.notifications.tokenValidationFailed'))
    removeCookie('accessToken')
    auth.loginFailure()
  }
}

onMounted(async () => {
  await validateToken()
})
</script>
