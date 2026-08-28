<template>
  <v-dialog v-model="dialogState" max-width="520">
    <v-form @submit.prevent="submit">
      <v-card>
        <v-card-title>{{ t('dialogs.vmProjectChange.title') }}</v-card-title>
        <v-card-text>
          <v-select
            v-model="projectId"
            data-testid="vm-project-change"
            :items="options"
            :loading="projectsLoading"
            item-title="title"
            item-value="value"
            :label="t('common.fields.project')"
            :rules="[r.required]"
          />
          <v-alert density="compact" type="info" variant="tonal">
            {{ t('dialogs.vmProjectChange.resourceNotice') }}
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogState = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">{{ t('dialogs.vmProjectChange.move') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { apiClient } from '@/api'
import type { components } from '@/api/openapi'
import { formatProjectName, getProjectList, type ProjectSummary } from '@/composables/project'
import notify, { apiErrorRef } from '@/composables/notify'
import { translationRef } from '@/composables/i18n'
import { useLocalizedRules } from '@/composables/rules'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ item: components['schemas']['DomainDetail'] }>()
const dialogState = defineModel({ default: false })
const emit = defineEmits<{ changed: [] }>()
const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()
const projects = ref<ProjectSummary[]>([])
const projectId = ref('')
const projectsLoading = ref(false)
const loading = ref(false)
const options = computed(() => projects.value.map(project => ({
  title: formatProjectName(project),
  value: project.id,
})))

async function loadProjects() {
  projectsLoading.value = true
  try {
    const response = await getProjectList({ limit: 0, page: 1 })
    projects.value = response.data
  } finally {
    projectsLoading.value = false
  }
}

async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid || !projectId.value) return
  loading.value = true
  try {
    const response = await apiClient.PATCH('/api/vms/{uuid}/project', {
      params: { path: { uuid: props.item.uuid } },
      body: { projectId: projectId.value },
    })
    if (!response.data) {
      notify('error', translationRef('dialogs.vmProjectChange.failed'), apiErrorRef(response.error))
      return
    }
    notify(
      'success',
      translationRef('dialogs.vmProjectChange.success'),
      translationRef('dialogs.vmProjectChange.successBody', { projectId: projectId.value }),
    )
    dialogState.value = false
    emit('changed')
  } catch {
    notify(
      'error',
      translationRef('dialogs.vmProjectChange.failed'),
      translationRef('dialogs.vmProjectChange.unreachable'),
    )
  } finally {
    loading.value = false
  }
}

watch(dialogState, open => {
  if (!open) return
  projectId.value = props.item.ownerProjectId ?? ''
  void loadProjects()
})
</script>
