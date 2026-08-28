<template>
  <v-dialog v-model="dialogState" max-width="520">
    <v-form @submit.prevent="submit">
      <v-card>
        <v-card-title>Move VM to Project</v-card-title>
        <v-card-text>
          <v-select
            v-model="projectId"
            data-testid="vm-project-change"
            :items="options"
            :loading="projectsLoading"
            item-title="title"
            item-value="value"
            label="Project"
            :rules="[r.required]"
          />
          <v-alert density="compact" type="info" variant="tonal">
            The destination Project must grant every storage and network resource currently used by this VM.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogState = false">Cancel</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">Move</v-btn>
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
import notify from '@/composables/notify'
import r from '@/composables/rules'

const props = defineProps<{ item: components['schemas']['DomainDetail'] }>()
const dialogState = defineModel({ default: false })
const emit = defineEmits<{ changed: [] }>()
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
      notify('error', 'Move VM failed', response.error)
      return
    }
    notify('success', 'VM moved', `The VM now belongs to Project #${projectId.value}.`)
    dialogState.value = false
    emit('changed')
  } catch {
    notify('error', 'Move VM failed', 'Unable to reach the VM service.')
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
