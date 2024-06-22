import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    tokenValidated: false,
    authed: false,
  }),
  actions: {
    loginSuccess(token: string) {
      this.token = token
      this.tokenValidated = true
      this.authed = true
    },
  },
})
