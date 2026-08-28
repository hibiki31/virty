<template>
  <div v-if="project">
    <v-card variant="flat">
      <v-card-title class="d-flex flex-wrap align-center ga-3">
        <v-icon icon="mdi-folder-account-outline" />
        <span>{{ formatProjectName(project) }}</span>
        <v-spacer />
        <v-btn
          v-if="isAdmin"
          color="error"
          prepend-icon="mdi-delete-outline"
          size="small"
          variant="tonal"
          :loading="deleteLoading"
          @click="queueDelete"
        >Delete</v-btn>
      </v-card-title>
      <v-card-subtitle>Shared ownership boundary for virtual machines and granted resources</v-card-subtitle>

      <v-card-text>
        <v-alert
          v-if="membershipChanged"
          class="mb-4"
          density="compact"
          type="info"
          variant="tonal"
        >
          Added members must sign in again before this Project appears in their token. Removed members lose access from their next request.
        </v-alert>

        <v-row>
          <v-col cols="12" md="4">
            <v-card title="Usage" variant="outlined" height="100%">
              <v-list density="compact">
                <v-list-item title="vCPU" :subtitle="`${project.usedCore} used`" />
                <v-list-item title="Memory" :subtitle="`${project.usedMemoryG} GiB used`" />
                <v-list-item title="Storage" :subtitle="`${project.usedStorageG} GiB used`" />
              </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card title="Limits (not enforced)" variant="outlined" height="100%">
              <v-list density="compact">
                <v-list-item title="vCPU" :subtitle="String(project.limits.core)" />
                <v-list-item title="Memory" :subtitle="`${project.limits.memoryG} GiB`" />
                <v-list-item title="Storage" :subtitle="`${project.limits.storageCapacityG} GiB`" />
              </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card title="Resources" variant="outlined" height="100%">
              <v-list density="compact">
                <v-list-item
                  title="Virtual machines"
                  :to="{ path: '/vms', query: { projectId } }"
                  prepend-icon="mdi-desktop-tower"
                />
                <v-list-item
                  title="Storage"
                  :to="{ path: '/storages', query: { projectId } }"
                  prepend-icon="mdi-database"
                />
                <v-list-item
                  title="Networks"
                  :to="{ path: '/networks', query: { projectId } }"
                  prepend-icon="mdi-wan"
                />
                <v-list-item
                  title="Images"
                  :to="{ path: '/images', query: { projectId } }"
                  prepend-icon="mdi-disc"
                />
                <v-list-item
                  title="Nodes"
                  :to="{ path: '/nodes', query: { projectId } }"
                  prepend-icon="mdi-server"
                />
              </v-list>
            </v-card>
          </v-col>
        </v-row>

        <v-card class="mt-5" title="Project name" variant="outlined">
          <v-card-text>
            <div v-if="canManageMembers" class="d-flex flex-wrap align-start ga-3">
              <v-text-field
                v-model="name"
                class="flex-grow-1"
                density="compact"
                label="Name"
                maxlength="64"
                :rules="[r.required, r.limitLength64]"
              />
              <v-btn color="primary" :loading="nameLoading" @click="saveName">Save</v-btn>
            </div>
            <span v-else>{{ project.name }}</span>
          </v-card-text>
        </v-card>

        <v-card class="mt-5" title="Members" variant="outlined">
          <v-card-text>
            <div class="d-flex flex-wrap ga-2">
              <v-chip
                v-for="member in project.members"
                :key="member.username"
                prepend-icon="mdi-account-outline"
                :closable="canManageMembers && project.members.length > 1"
                @click:close="removeMember(member.username)"
              >{{ member.username }}</v-chip>
            </div>

            <div v-if="canManageMembers" class="d-flex flex-wrap align-start ga-3 mt-4">
              <v-autocomplete
                v-model="newMember"
                class="flex-grow-1"
                clearable
                density="compact"
                :items="memberCandidates"
                :loading="candidateLoading"
                item-title="username"
                item-value="username"
                label="Add member"
                no-filter
                @update:search="searchMemberCandidates"
              />
              <v-btn
                color="primary"
                :disabled="!newMember"
                :loading="memberLoading"
                @click="addMember"
              >Add</v-btn>
            </div>
          </v-card-text>
        </v-card>

        <v-card class="mt-5" title="Resource grants" variant="outlined">
          <v-card-text>
            <template v-if="isAdmin && editingGrants">
              <v-select
                v-model="grants.storagePoolIds"
                :items="storagePoolOptions"
                item-title="name"
                item-value="id"
                label="Storage pools"
                multiple
                chips
              />
              <v-select
                v-model="grants.networkPoolIds"
                :items="networkPoolOptions"
                item-title="name"
                item-value="id"
                label="Network pools"
                multiple
                chips
              />
              <v-select
                v-model="grants.flavorIds"
                :items="flavorOptions"
                item-title="name"
                item-value="id"
                label="Flavors"
                multiple
                chips
              />
              <div class="d-flex justify-end ga-2">
                <v-btn variant="text" @click="editingGrants = false">Cancel</v-btn>
                <v-btn color="primary" :loading="grantsLoading" @click="saveGrants">Save grants</v-btn>
              </div>
            </template>
            <template v-else>
              <div class="mb-3">
                <div class="text-caption text-medium-emphasis">Storage pools</div>
                <v-chip v-for="pool in project.storagePools" :key="pool.id" class="ma-1" size="small">
                  {{ pool.name }} (#{{ pool.id }})
                </v-chip>
                <span v-if="project.storagePools.length === 0">None</span>
              </div>
              <div class="mb-3">
                <div class="text-caption text-medium-emphasis">Network pools</div>
                <v-chip v-for="pool in project.networkPools" :key="pool.id" class="ma-1" size="small">
                  {{ pool.name }} (#{{ pool.id }})
                </v-chip>
                <span v-if="project.networkPools.length === 0">None</span>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Flavors</div>
                <v-chip v-for="flavor in project.flavors" :key="flavor.id" class="ma-1" size="small">
                  {{ flavor.name }} (#{{ flavor.id }})
                </v-chip>
                <span v-if="project.flavors.length === 0">None</span>
              </div>
              <v-btn
                v-if="isAdmin"
                class="mt-4"
                prepend-icon="mdi-pencil-outline"
                variant="tonal"
                @click="startGrantEdit"
              >Edit grants</v-btn>
            </template>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>
  </div>

  <v-card v-else-if="loading" aria-busy="true">
    <v-skeleton-loader type="article, article" />
  </v-card>
</template>

<route lang="yaml">
meta:
  title: Virty - Project
</route>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { components } from '@/api/openapi'
import { hasAdminScope, hasScope } from '@/composables/auth'
import notify, { notifyTask } from '@/composables/notify'
import {
  addProjectMember,
  deleteProject,
  formatProjectName,
  getProject,
  getProjectMemberCandidates,
  getProjectResourceGrantCandidates,
  removeProjectMember,
  replaceProjectResourceGrants,
  updateProjectName,
  type ProjectDetail,
  type ProjectResourceGrantsUpdate,
} from '@/composables/project'
import r from '@/composables/rules'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const projectId = computed(() => 'id' in route.params ? String(route.params.id) : '')
const isAdmin = hasAdminScope(auth.scopes)
const canManageMembers = computed(() =>
  hasScope(auth.scopes, 'project.manage') && auth.projects.includes(projectId.value)
)

const loading = ref(false)
const nameLoading = ref(false)
const memberLoading = ref(false)
const deleteLoading = ref(false)
const grantsLoading = ref(false)
const candidateLoading = ref(false)
const membershipChanged = ref(false)
const editingGrants = ref(false)
const project = ref<ProjectDetail>()
const name = ref('')
const newMember = ref<string | null>(null)
const memberCandidates = ref<components['schemas']['ProjectMember'][]>([])
const grants = reactive<ProjectResourceGrantsUpdate>({
  storagePoolIds: [],
  networkPoolIds: [],
  flavorIds: [],
})
const storagePoolOptions = ref<components['schemas']['ProjectResourceReference'][]>([])
const networkPoolOptions = ref<components['schemas']['ProjectResourceReference'][]>([])
const flavorOptions = ref<components['schemas']['ProjectResourceReference'][]>([])

async function reload() {
  loading.value = true
  try {
    project.value = await getProject(projectId.value)
    name.value = project.value.name
    window.document.title = `Virty - ${formatProjectName(project.value)}`
  } catch (error) {
    notify('error', 'Load Project failed', error instanceof Error ? error.message : undefined)
  } finally {
    loading.value = false
  }
}

async function saveName() {
  if (!name.value.trim() || name.value.trim().length > 64) return
  nameLoading.value = true
  try {
    project.value = await updateProjectName(projectId.value, { name: name.value.trim() })
    notify('success', 'Project updated', 'The Project name was updated.')
  } catch (error) {
    notify('error', 'Update Project failed', error instanceof Error ? error.message : undefined)
  } finally {
    nameLoading.value = false
  }
}

async function searchMemberCandidates(search: string) {
  if (!canManageMembers.value) return
  candidateLoading.value = true
  try {
    const response = await getProjectMemberCandidates(projectId.value, {
      nameLike: search || '',
      limit: 20,
      page: 1,
    })
    memberCandidates.value = response.data
  } finally {
    candidateLoading.value = false
  }
}

async function addMember() {
  if (!newMember.value) return
  memberLoading.value = true
  try {
    project.value = await addProjectMember(projectId.value, newMember.value)
    newMember.value = null
    membershipChanged.value = true
    await searchMemberCandidates('')
  } catch (error) {
    notify('error', 'Add member failed', error instanceof Error ? error.message : undefined)
  } finally {
    memberLoading.value = false
  }
}

async function removeMember(username: string) {
  memberLoading.value = true
  try {
    project.value = await removeProjectMember(projectId.value, username)
    membershipChanged.value = true
  } catch (error) {
    notify('error', 'Remove member failed', error instanceof Error ? error.message : undefined)
  } finally {
    memberLoading.value = false
  }
}

async function loadGrantOptions() {
  const candidates = await getProjectResourceGrantCandidates(projectId.value)
  storagePoolOptions.value = candidates.storagePools
  networkPoolOptions.value = candidates.networkPools
  flavorOptions.value = candidates.flavors
}

async function startGrantEdit() {
  if (!project.value) return
  grants.storagePoolIds = [...project.value.resourceGrants.storagePoolIds]
  grants.networkPoolIds = [...project.value.resourceGrants.networkPoolIds]
  grants.flavorIds = [...project.value.resourceGrants.flavorIds]
  editingGrants.value = true
  try {
    await loadGrantOptions()
  } catch {
    notify('error', 'Load resource pools failed', 'Grant candidates could not be loaded.')
  }
}

async function saveGrants() {
  grantsLoading.value = true
  try {
    project.value = await replaceProjectResourceGrants(projectId.value, {
      storagePoolIds: [...grants.storagePoolIds],
      networkPoolIds: [...grants.networkPoolIds],
      flavorIds: [...grants.flavorIds],
    })
    editingGrants.value = false
    notify('success', 'Resource grants updated', 'The Project resource grants were replaced.')
  } catch (error) {
    notify('error', 'Update grants failed', error instanceof Error ? error.message : undefined)
  } finally {
    grantsLoading.value = false
  }
}

async function queueDelete() {
  if (!window.confirm(`Delete ${project.value ? formatProjectName(project.value) : projectId.value}?`)) return
  deleteLoading.value = true
  try {
    const tasks = await deleteProject(projectId.value)
    notifyTask(tasks[0]?.uuid)
    await router.push('/projects')
  } catch (error) {
    notify('error', 'Delete Project failed', error instanceof Error ? error.message : undefined)
  } finally {
    deleteLoading.value = false
  }
}

useReloadListener(() => { void reload() })
onMounted(async () => {
  await reload()
  if (canManageMembers.value) await searchMemberCandidates('')
})
</script>
