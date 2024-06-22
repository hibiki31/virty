/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import { setupLayouts } from 'virtual:generated-layouts'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  extendRoutes: setupLayouts,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  console.debug('from: ', from.name, 'to: ', to.name)
  console.debug('authed: ', auth.authed)

  // ログインしているのにログインページに行く場合
  if (auth.authed && to.name === '/login') {
    next({
      name: 'VideoList',
    })
  }
  // 認証が必要なページに未認証でアクセスした場合
  else if (!auth.authed && to.matched.some((record) => record.meta.requiresAuth)) {
    next({
      name: 'Login',
    })
  }
  // ログイン済み、ログイン不要の場合の通常遷移
  else {
    next()
  }
})

export default router
