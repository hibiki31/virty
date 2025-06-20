import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    baseURL: [null, undefined].includes(import.meta.env.VITE_API_BASE_URL) ? '' : import.meta.env.VITE_API_BASE_URL,
    token: '',
    tokenValidated: false,
    authed: false,
  }),
  actions: {
    loginSuccess (token: string) {
      this.token = token
      this.tokenValidated = true
      this.authed = true
    },
  },
})
