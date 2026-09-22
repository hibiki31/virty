import { useProjectFilter } from '@/composables/projectFilter'
import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it } from 'vitest'

async function setup(path: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push(path)
  let filter!: ReturnType<typeof useProjectFilter>
  const wrapper = mount(defineComponent({
    setup() {
      filter = useProjectFilter()
      return () => null
    },
  }), { global: { plugins: [router] } })
  return { filter, router, wrapper }
}

describe('共通Project filter', () => {
  it('切替・解除で他のqueryとhashを保ち、履歴と直接URLの値に追従する', async () => {
    const { filter, router, wrapper } = await setup('/vms?nameLike=demo#list')
    expect(filter.projectId.value).toBeNull()

    await filter.updateProjectFilter('a1b2c3')
    expect(router.currentRoute.value.query).toEqual({ nameLike: 'demo', projectId: 'a1b2c3' })
    expect(router.currentRoute.value.hash).toBe('#list')

    await router.push('/nodes?projectId=d4e5f6')
    expect(filter.projectId.value).toBe('d4e5f6')
    router.back()
    await flushPromises()
    expect(filter.projectId.value).toBe('a1b2c3')

    await filter.updateProjectFilter(null)
    expect(router.currentRoute.value.query).toEqual({ nameLike: 'demo' })
    expect(router.currentRoute.value.hash).toBe('#list')
    expect(filter.projectId.value).toBeNull()
    wrapper.unmount()
  })

  it.each(['/vms?projectId', '/vms?projectId=', '/vms?projectId=a&projectId=b'])(
    '単一IDではないURLを未選択として扱う: %s', async path => {
      const { filter, wrapper } = await setup(path)
      expect(filter.projectId.value).toBeNull()
      wrapper.unmount()
    },
  )
})
