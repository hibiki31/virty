<template>
  <v-select
    :model-value="modelValue"
    :items="options"
    :loading="loading"
    clearable
    density="compact"
    hide-details
    item-title="title"
    item-value="value"
    :label="t('common.fields.project')"
    :aria-label="t('common.fields.project')"
    :title="options.find(option => option.value === modelValue)?.title"
    persistent-placeholder
    variant="solo-filled"
    @update:model-value="value => emit('update:modelValue', value || null)"
  />
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { formatProjectName, getProjectList, type ProjectSummary } from '@/composables/project'
import { useI18n } from 'vue-i18n'

defineProps<{ modelValue: string | null | undefined }>()
const emit = defineEmits<{ 'update:modelValue': [value: string | null] }>()
const { t } = useI18n({ useScope: 'global' })

const loading = ref(false)
const projects = ref<ProjectSummary[]>([])
const options = computed(() => projects.value.map(project => ({
  title: formatProjectName(project),
  value: project.id,
})))

onMounted(async () => {
  loading.value = true
  try {
    const page = await getProjectList({
      limit: 0,
      page: 1,
    })
    projects.value = page.data
  } catch {
    projects.value = []
  } finally {
    loading.value = false
  }
})
</script>
