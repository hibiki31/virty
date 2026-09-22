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
        >{{ t('common.actions.delete') }}</v-btn>
      </v-card-title>
      <v-card-subtitle>{{ t('pages.projectDetail.subtitle') }}</v-card-subtitle>

      <v-card-text>
        <v-alert
          v-if="membershipChanged"
          class="mb-4"
          density="compact"
          type="info"
          variant="tonal"
        >
          {{ t('pages.projectDetail.membershipChanged') }}
        </v-alert>

        <v-row>
          <v-col cols="12" md="4">
            <v-card :title="t('pages.projectDetail.sections.usage')" variant="outlined" height="100%">
              <v-list density="compact">
                <v-list-item :title="t('pages.projectDetail.values.vcpu')" :subtitle="t('pages.projectDetail.values.used', { value: formatNumber(project.usedCore) })" />
                <v-list-item :title="t('common.fields.memory')" :subtitle="t('pages.projectDetail.values.gibUsed', { value: formatNumber(project.usedMemoryG) })" />
                <v-list-item :title="t('common.fields.storage')" :subtitle="t('pages.projectDetail.values.gibUsed', { value: formatNumber(project.usedStorageG) })" />
              </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card :title="t('pages.projectDetail.sections.limits')" variant="outlined" height="100%">
              <v-list density="compact">
                <v-list-item :title="t('pages.projectDetail.values.vcpu')" :subtitle="formatNumber(project.limits.core)" />
                <v-list-item :title="t('common.fields.memory')" :subtitle="t('pages.projectDetail.values.gib', { value: formatNumber(project.limits.memoryG) })" />
                <v-list-item
                  :title="t('common.fields.storage')"
                  :subtitle="project.limits.storageCapacityG == null
                    ? t('common.values.unavailable')
                    : t('pages.projectDetail.values.gib', { value: formatNumber(project.limits.storageCapacityG) })"
                />
              </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card :title="t('pages.projectDetail.sections.resources')" variant="outlined" height="100%">
              <v-list density="compact">
                <v-list-item
                  :title="t('navigation.vms')"
                  :to="{ path: '/vms', query: { projectId } }"
                  prepend-icon="mdi-desktop-tower"
                />
                <v-list-item
                  :title="t('navigation.storages')"
                  :to="{ path: '/storages', query: { projectId } }"
                  prepend-icon="mdi-database"
                />
                <v-list-item
                  :title="t('navigation.networks')"
                  :to="{ path: '/networks', query: { projectId } }"
                  prepend-icon="mdi-wan"
                />
                <v-list-item
                  :title="t('navigation.images')"
                  :to="{ path: '/images', query: { projectId } }"
                  prepend-icon="mdi-disc"
                />
                <v-list-item
                  :title="t('navigation.nodes')"
                  :to="{ path: '/nodes', query: { projectId } }"
                  prepend-icon="mdi-server"
                />
              </v-list>
            </v-card>
          </v-col>
        </v-row>

        <v-card class="mt-5" :title="t('pages.projectDetail.sections.name')" variant="outlined">
          <v-card-text>
            <div v-if="canManageMembers" class="d-flex flex-wrap align-start ga-3">
              <v-text-field
                v-model="name"
                class="flex-grow-1"
                density="compact"
                :label="t('common.fields.name')"
                maxlength="64"
                :rules="[r.required, r.limitLength64]"
              />
              <v-btn color="primary" :loading="nameLoading" @click="saveName">{{ t('common.actions.save') }}</v-btn>
            </div>
            <span v-else>{{ project.name }}</span>
          </v-card-text>
        </v-card>

        <v-card class="mt-5" :title="t('pages.projectDetail.sections.members')" variant="outlined">
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
                :label="t('pages.projectDetail.members.add')"
                no-filter
                @update:search="searchMemberCandidates"
              />
              <v-btn
                color="primary"
                :disabled="!newMember"
                :loading="memberLoading"
                @click="addMember"
              >{{ t('common.actions.add') }}</v-btn>
            </div>
          </v-card-text>
        </v-card>

        <v-card class="mt-5" :title="t('pages.projectDetail.sections.grants')" variant="outlined">
          <v-card-text>
            <template v-if="isAdmin && editingGrants">
              <v-checkbox
                :model-value="allSelected(grants.storagePoolIds, storagePoolOptions)"
                :label="t('pages.projectDetail.grants.allStoragePools')"
                hide-details
                @update:model-value="grants.storagePoolIds = selectAll($event, storagePoolOptions)"
              />
              <v-select
                v-model="grants.storagePoolIds"
                data-testid="project-grant-storage-pools"
                :items="storagePoolOptions"
                item-title="name"
                item-value="id"
                :label="t('pages.projectDetail.grants.storagePools')"
                multiple
                chips
              />
              <v-checkbox
                :model-value="allSelected(grants.networkPoolIds, networkPoolOptions)"
                :label="t('pages.projectDetail.grants.allNetworkPools')"
                hide-details
                @update:model-value="grants.networkPoolIds = selectAll($event, networkPoolOptions)"
              />
              <v-select
                v-model="grants.networkPoolIds"
                data-testid="project-grant-network-pools"
                :items="networkPoolOptions"
                item-title="name"
                item-value="id"
                :label="t('pages.projectDetail.grants.networkPools')"
                multiple
                chips
              />
              <v-checkbox
                :model-value="allSelected(grants.flavorIds, flavorOptions)"
                :label="t('pages.projectDetail.grants.allFlavors')"
                hide-details
                @update:model-value="grants.flavorIds = selectAll($event, flavorOptions)"
              />
              <v-select
                v-model="grants.flavorIds"
                data-testid="project-grant-flavors"
                :items="flavorOptions"
                item-title="name"
                item-value="id"
                :label="t('pages.projectDetail.grants.flavors')"
                multiple
                chips
              />
              <div class="d-flex justify-end ga-2">
                <v-btn variant="text" @click="editingGrants = false">{{ t('common.actions.cancel') }}</v-btn>
                <v-btn color="primary" :loading="grantsLoading" @click="saveGrants">{{ t('pages.projectDetail.grants.save') }}</v-btn>
              </div>
            </template>
            <template v-else>
              <div class="mb-3">
                <div class="text-caption text-medium-emphasis">{{ t('pages.projectDetail.grants.storagePools') }}</div>
                <v-chip v-for="pool in project.storagePools" :key="pool.id" class="ma-1" size="small">
                  {{ pool.name }} (#{{ pool.id }})
                </v-chip>
                <span v-if="project.storagePools.length === 0">{{ t('common.values.none') }}</span>
              </div>
              <div class="mb-3">
                <div class="text-caption text-medium-emphasis">{{ t('pages.projectDetail.grants.networkPools') }}</div>
                <v-chip v-for="pool in project.networkPools" :key="pool.id" class="ma-1" size="small">
                  {{ pool.name }} (#{{ pool.id }})
                </v-chip>
                <span v-if="project.networkPools.length === 0">{{ t('common.values.none') }}</span>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">{{ t('pages.projectDetail.grants.flavors') }}</div>
                <v-chip v-for="flavor in project.flavors" :key="flavor.id" class="ma-1" size="small">
                  {{ flavor.name }} (#{{ flavor.id }})
                </v-chip>
                <span v-if="project.flavors.length === 0">{{ t('common.values.none') }}</span>
              </div>
              <v-btn
                v-if="isAdmin"
                class="mt-4"
                prepend-icon="mdi-pencil-outline"
                variant="tonal"
                @click="startGrantEdit"
              >{{ t('pages.projectDetail.grants.edit') }}</v-btn>
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
  titleKey: pages.projectDetail.documentTitle
</route>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { components } from '@/api/openapi'
import { hasAdminScope, hasScope } from '@/composables/auth'
import notify, { notificationContentFromError, notifyTask } from '@/composables/notify'
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
import { formatNumber, translationRef, useLocalizedDocumentTitle } from '@/composables/i18n'
import { useLocalizedRules } from '@/composables/rules'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()
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
type GrantOption = components['schemas']['ProjectResourceReference']

function allSelected(selected: number[], options: GrantOption[]): boolean {
  return options.length > 0 && options.every(option => selected.includes(option.id))
}

function selectAll(value: boolean | null, options: GrantOption[]): number[] {
  return value ? options.map(option => option.id) : []
}

useLocalizedDocumentTitle(() => project.value
  ? formatProjectName(project.value)
  : t('pages.projectDetail.documentTitle'))

async function reload() {
  loading.value = true
  try {
    project.value = await getProject(projectId.value, isAdmin)
    name.value = project.value.name
  } catch (error) {
    notify('error', translationRef('pages.projectDetail.notifications.loadFailed'), notificationContentFromError(error))
  } finally {
    loading.value = false
  }
}

async function saveName() {
  if (!name.value.trim() || name.value.trim().length > 64) return
  nameLoading.value = true
  try {
    project.value = await updateProjectName(projectId.value, { name: name.value.trim() })
    notify('success', translationRef('pages.projectDetail.notifications.updated'), translationRef('pages.projectDetail.notifications.nameUpdated'))
  } catch (error) {
    notify('error', translationRef('pages.projectDetail.notifications.updateFailed'), notificationContentFromError(error))
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
    notify('error', translationRef('pages.projectDetail.notifications.addMemberFailed'), notificationContentFromError(error))
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
    notify('error', translationRef('pages.projectDetail.notifications.removeMemberFailed'), notificationContentFromError(error))
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
    notify('error', translationRef('pages.projectDetail.notifications.loadPoolsFailed'), translationRef('pages.projectDetail.notifications.candidatesUnavailable'))
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
    notify('success', translationRef('pages.projectDetail.notifications.grantsUpdated'), translationRef('pages.projectDetail.notifications.grantsUpdatedBody'))
  } catch (error) {
    notify('error', translationRef('pages.projectDetail.notifications.updateGrantsFailed'), notificationContentFromError(error))
  } finally {
    grantsLoading.value = false
  }
}

async function queueDelete() {
  if (!window.confirm(t('pages.projectDetail.deleteConfirm', {
    project: project.value ? formatProjectName(project.value) : projectId.value,
  }))) return
  deleteLoading.value = true
  try {
    const tasks = await deleteProject(projectId.value)
    notifyTask(tasks[0]?.uuid)
    await router.push('/projects')
  } catch (error) {
    notify('error', translationRef('pages.projectDetail.notifications.deleteFailed'), notificationContentFromError(error))
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
