import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useProjectFilter() {
  const route = useRoute()
  const router = useRouter()
  const projectId = computed(() =>
    typeof route.query.projectId === 'string' ? route.query.projectId || null : null,
  )

  async function updateProjectFilter(value: string | null): Promise<void> {
    const query = { ...route.query }
    if (value) query.projectId = value
    else delete query.projectId
    await router.replace({ query, hash: route.hash })
  }

  return { projectId, updateProjectFilter }
}
