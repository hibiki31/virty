<template>
  <v-dialog v-model="dialogState" data-testid="vm-create-dialog" width="calc(100% - 32px)" max-width="1100">
    <v-form class="vm-create-dialog__form" @submit.prevent="submit">
      <v-card class="vm-create-dialog">
        <v-card-title class="d-flex align-center px-4 py-3">
          <span class="text-h6">{{ t('dialogs.vmAdd.title') }}</span>
          <v-btn class="ml-auto" icon="mdi-close" size="small" variant="text" :aria-label="t('common.actions.close')"
            @click="dialogState = false"></v-btn>
        </v-card-title>
        <v-divider></v-divider>

        <v-card-text class="vm-create-dialog__body pa-4">
          <section class="vm-create-dialog__section">
            <h3 class="vm-create-dialog__section-title">{{ t('dialogs.vmAdd.basic') }}</h3>
            <v-alert v-if="!projectsLoading && itemsProjects.length === 0" class="mb-3" density="compact"
              type="warning" variant="tonal">
              {{ t('dialogs.vmAdd.projectRequired') }}
            </v-alert>
            <v-row class="ma-n1">
              <v-col cols="12" md="4" class="pa-1">
                <v-select v-model="postData.projectId" data-testid="vm-project" variant="outlined" density="compact"
                  :label="t('common.fields.project')" hide-details="auto" :items="projectOptions" :loading="projectsLoading"
                  :rules="[r.required]" item-title="title" item-value="value"></v-select>
              </v-col>
              <v-col cols="12" md="4" class="pa-1">
                <v-text-field v-model="postData.name" data-testid="vm-name" variant="outlined" density="compact" :label="t('common.fields.name')"
                  hide-details="auto"
                  :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                  @change="() => { if (postData.cloudInit) { postData.cloudInit.hostname = postData.name } }"></v-text-field>
              </v-col>
              <v-col cols="12" md="4" class="pa-1">
                <v-select v-model="postData.nodeName" data-testid="vm-node" variant="outlined" density="compact" :label="t('common.fields.node')"
                  hide-details="auto" :items="itemsNodes.data" :loading="resourcesLoading" :disabled="!postData.projectId"
                  :rules="[r.required]" item-title="name"
                  item-value="name"></v-select>
              </v-col>
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-select v-model="postData.memoryMegaByte" variant="outlined" density="compact" :label="t('common.fields.memory')"
                  hide-details="auto" :items="itemsMemory" item-title="title" item-value="value"
                  :rules="[r.required]"></v-select>
              </v-col>
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-select v-model="postData.cpu" variant="outlined" density="compact" :label="t('common.fields.cpu')"
                  hide-details="auto" :items="localizedCpuItems" :rules="[r.required]"></v-select>
              </v-col>
            </v-row>
          </section>

          <section class="vm-create-dialog__section">
            <div class="d-flex align-center ga-3 mb-2">
              <h3 class="vm-create-dialog__section-title mb-0">{{ t('common.fields.storage') }}</h3>
              <span v-if="postData.disks[0]?.type === 'empty'" class="text-caption text-medium-emphasis">
                {{ t('dialogs.vmAdd.isoHelp') }}
              </span>
            </div>
            <v-row v-for="(disk, index) in postData.disks" :key="index" class="ma-n1">
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-select v-model="disk.type" variant="outlined" density="compact" :label="t('common.fields.mode')" hide-details="auto"
                  :items="diskModeItems"
                  :rules="[r.required]"></v-select>
              </v-col>
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-text-field v-model="disk.sizeGigaByte" variant="outlined" density="compact" :label="t('dialogs.vmAdd.sizeGb')"
                  hide-details="auto" :rules="[r.required]"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" :md="disk.type === 'copy' ? 3 : 8" class="pa-1">
                <v-select v-model="disk.savePoolUuid" data-testid="vm-destination-pool" variant="outlined" density="compact" :label="t('dialogs.vmAdd.destinationPool')"
                  hide-details="auto" :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)"
                  :disabled="!postData.projectId" :loading="resourcesLoading"
                  :rules="[r.required]" item-title="name" item-value="uuid"></v-select>
              </v-col>
              <v-col v-if="disk.type === 'copy'" cols="12" sm="6" md="2" class="pa-1">
                <v-select v-model="disk.originalPoolUuid" variant="outlined" density="compact" :label="t('dialogs.vmAdd.sourcePool')"
                  hide-details="auto" :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)"
                  :disabled="!postData.projectId" :loading="resourcesLoading"
                  :rules="[r.required]" item-title="name" item-value="uuid"></v-select>
              </v-col>
              <v-col v-if="disk.type === 'copy'" cols="12" sm="6" md="3" class="pa-1">
                <v-select v-model="disk.originalName" variant="outlined" density="compact" :label="t('dialogs.vmAdd.sourceImage')"
                  hide-details="auto" :items="itemsImages.data.filter(x => x.storageUuid === disk.originalPoolUuid)"
                  :disabled="!postData.projectId" :loading="resourcesLoading"
                  :rules="[r.required]" item-title="name" item-value="name"></v-select>
              </v-col>
            </v-row>
          </section>

          <section class="vm-create-dialog__section">
            <div class="d-flex align-center mb-2">
              <h3 class="vm-create-dialog__section-title mb-0">{{ t('common.fields.network') }}</h3>
              <v-btn class="ml-auto" prepend-icon="mdi-plus" size="small" variant="text"
                @click="addInterface">{{ t('dialogs.vmAdd.addInterface') }}</v-btn>
            </div>
            <v-row v-for="(nic, index) in postData.interface" :key="index" class="ma-n1 align-center">
              <v-col cols="10" :md="checkOVS(nic.networkUuid) ? 6 : 11" class="pa-1">
                <v-select v-model="nic.networkUuid" data-testid="vm-network" variant="outlined" density="compact" :label="t('common.fields.network')"
                  hide-details="auto" :items="itemsNetworks.data.filter(x => x.nodeName === postData.nodeName)"
                  :disabled="!postData.projectId" :loading="resourcesLoading"
                  item-title="name" item-value="uuid" :rules="[r.required]"></v-select>
              </v-col>
              <v-col v-if="checkOVS(nic.networkUuid)" cols="10" md="5" class="pa-1">
                <v-select v-model="nic.port" data-testid="vm-network-port" variant="outlined" density="compact" :label="t('common.fields.port')" hide-details="auto"
                  :items="itemsPort(nic.networkUuid)" item-title="title" item-value="value"
                  :rules="[r.required]"></v-select>
              </v-col>
              <v-col cols="2" md="1" class="pa-1 text-right">
                <v-btn icon="mdi-delete-outline" size="small" variant="text" :aria-label="t('dialogs.vmAdd.removeInterface')"
                  @click="deleteInterface(index)"></v-btn>
              </v-col>
            </v-row>
          </section>

          <section class="vm-create-dialog__section">
            <div class="d-flex align-center">
              <h3 class="vm-create-dialog__section-title mb-0">{{ t('dialogs.vmAdd.cloudInit') }}</h3>
              <v-checkbox data-testid="cloud-init-toggle" class="ml-auto flex-grow-0" density="compact" hide-details
                :model-value="postData.cloudInit !== null" :label="t('dialogs.vmAdd.enable')" color="primary"
                @update:model-value="togleCloudInit"></v-checkbox>
            </div>

            <div v-if="postData.cloudInit" class="mt-2">
              <v-row class="ma-n1 align-center">
                <v-col cols="12" md="7" class="pa-1">
                  <v-text-field v-model="postData.cloudInit.hostname" variant="outlined" density="compact"
                    :label="t('dialogs.vmAdd.hostName')" hide-details="auto"
                    :rules="[r.required, r.limitLength64, r.characterRestrictions]"></v-text-field>
                </v-col>
                <v-col cols="12" md="5" class="pa-1">
                  <v-tabs data-testid="cloud-init-tabs" v-model="cloudInitTab" density="compact" color="primary"
                    grow>
                    <v-tab value="simple" @click="cloudInitTab = 'simple'">{{ t('dialogs.vmAdd.simpleForm') }}</v-tab>
                    <v-tab value="yaml" @click="cloudInitTab = 'yaml'">{{ t('dialogs.vmAdd.yaml') }}</v-tab>
                  </v-tabs>
                </v-col>
              </v-row>

              <v-window v-model="cloudInitTab">
                <v-window-item value="simple">
                  <v-alert class="my-2 py-2" density="compact" type="warning" variant="tonal">
                    {{ t('dialogs.vmAdd.cloudInitWarning') }}
                  </v-alert>

                  <v-row class="ma-n1">
                    <v-col cols="12" md="6" class="pa-1">
                      <v-text-field data-testid="cloud-init-username" v-model="cloudInitForm.username"
                        variant="outlined" density="compact" :label="t('dialogs.vmAdd.initialUsername')" hide-details="auto"
                        :hint="t('dialogs.vmAdd.unavailableDefaultUser')"></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-text-field data-testid="cloud-init-password" v-model="cloudInitForm.password"
                        variant="outlined" density="compact" :label="t('common.fields.password')" hide-details="auto" type="password"
                        autocomplete="new-password"></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-checkbox data-testid="cloud-init-password-expires" v-model="cloudInitForm.passwordExpires"
                        density="compact" hide-details :label="t('dialogs.vmAdd.passwordChange')"
                        color="primary"></v-checkbox>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-checkbox data-testid="cloud-init-ssh-password-authentication"
                        v-model="cloudInitForm.sshPasswordAuthentication" density="compact" hide-details
                        :label="t('dialogs.vmAdd.sshPassword')" color="primary"></v-checkbox>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-select data-testid="cloud-init-saved-public-keys" v-model="cloudInitForm.selectedPublicKeys"
                        variant="outlined" density="compact" :label="t('dialogs.vmAdd.savedKeys')" hide-details="auto"
                        :items="savedPublicKeys" item-title="name" item-value="publickey" multiple chips closable-chips
                        :loading="savedPublicKeysLoading" :no-data-text="t('dialogs.vmAdd.noSavedKeys')"></v-select>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-textarea data-testid="cloud-init-manual-public-keys" v-model="cloudInitForm.manualPublicKeys"
                        variant="outlined" density="compact" :label="t('dialogs.vmAdd.additionalKeys')" hide-details="auto"
                        :hint="t('dialogs.vmAdd.oneKeyPerLine')" rows="2" auto-grow max-rows="4"></v-textarea>
                    </v-col>
                    <v-col cols="12" class="pa-1">
                      <v-textarea data-testid="cloud-init-script" v-model="cloudInitForm.script" variant="outlined"
                        density="compact" :label="t('dialogs.vmAdd.initialScript')" hide-details="auto" rows="2" auto-grow
                        max-rows="5"></v-textarea>
                    </v-col>
                  </v-row>

                  <v-alert v-if="savedPublicKeysError" data-testid="saved-public-keys-error" class="mt-2 py-2"
                    density="compact" type="warning" variant="tonal">{{ t('dialogs.vmAdd.savedKeysFailed') }}</v-alert>
                  <v-alert v-if="cloudInitFormDirty" data-testid="cloud-init-dirty-warning" class="mt-2 py-2"
                    density="compact" type="warning" variant="tonal">
                    {{ t('dialogs.vmAdd.cloudInitDirty') }}
                  </v-alert>
                  <v-alert v-if="cloudInitFormError" data-testid="cloud-init-form-error" class="mt-2 py-2"
                    density="compact" type="error" variant="tonal" style="white-space: pre-line">
                    {{ cloudInitFormError }}
                  </v-alert>
                  <div class="text-right mt-2">
                    <v-btn data-testid="cloud-init-apply" color="primary" size="small" variant="tonal"
                      @click="applyCloudInitForm">{{ t('dialogs.vmAdd.applyYaml') }}</v-btn>
                  </div>
                </v-window-item>

                <v-window-item value="yaml">
                  <v-textarea data-testid="cloud-init-yaml" class="text-caption mt-2" variant="outlined"
                    density="compact" clearable rows="10" :model-value="postData.cloudInit.userData"
                    clear-icon="mdi-close-circle" :label="t('dialogs.vmAdd.userData')" :error-messages="cloudInitYamlError"
                    style="white-space: pre-line" @update:model-value="updateCloudInitUserData"></v-textarea>
                </v-window-item>
              </v-window>
            </div>
          </section>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions class="justify-end px-4 py-2">
          <v-btn data-testid="vm-create-cancel" variant="text" @click="dialogState = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn data-testid="vm-create-submit" color="primary" type="submit" :loading="loading"
            :disabled="itemsProjects.length === 0">{{ t('common.actions.create') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref, toRaw, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useLocalizedRules } from '@/composables/rules';
import { itemsCPU, itemsMemory } from '@/composables/vm'
import type { bodyPostVM } from '@/composables/vm';
import type { typeListNode } from '@/composables/nodes';
import { initNodeList, getNode } from '@/composables/nodes';

import type { typeListNetwork, typeListNetworkQuery } from '@/composables/network';
import { initNetworkList, getNetworkList } from '@/composables/network';

import type { typeListStorageQuery } from '@/composables/storage';
import { initStorageList, getStorageList } from '@/composables/storage';

import type { typeListImage, typeListImageQuery } from '@/composables/image';
import { initImageList, getImageList } from '@/composables/image';
import { apiClient } from '@/api';
import notify, { apiErrorRef, notifyTask } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import type { schemas } from '@/composables/schemas';
import {
  EMPTY_CLOUD_CONFIG,
  createCloudInitFormState,
  formatCloudInitErrors,
  mergeCloudInitForm,
  validateCloudInitYaml,
} from '@/composables/cloudInit';
import type { CloudInitFormState } from '@/composables/cloudInit';
import type { TranslationRef } from '@/composables/i18n';
import { useAuthStore } from '@/stores/auth';
import { formatProjectName, getProjectList, type ProjectSummary } from '@/composables/project';

const { locale, t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()
const loading = ref(false)
const projectsLoading = ref(false)
const resourcesLoading = ref(false)
const dialogState = defineModel({ default: false })

const itemsNodes = ref<typeListNode>(initNodeList)
const itemsNetworks = ref<typeListNetwork>(initNetworkList)
const itemsStorages = ref<schemas['StoragePage']>(initStorageList)
const itemsImages = ref<typeListImage>(initImageList)
const itemsProjects = ref<ProjectSummary[]>([])
const projectOptions = computed(() => itemsProjects.value.map(project => ({
  title: formatProjectName(project),
  value: project.id,
})))
const cloudInitTab = ref<'simple' | 'yaml'>('simple')
const cloudInitForm = reactive<CloudInitFormState>(createCloudInitFormState())
const cloudInitFormSnapshot = ref(JSON.stringify(toRaw(cloudInitForm)))
const cloudInitFormErrors = ref<TranslationRef[]>([])
const cloudInitYamlErrors = ref<TranslationRef[]>([])
const savedPublicKeys = ref<schemas['UserPublickey'][]>([])
const savedPublicKeysLoading = ref(false)
const savedPublicKeysError = ref(false)
const savedPublicKeysLoadAttempted = ref(false)

const diskModeItems = computed(() => [
  { title: t('dialogs.vmAdd.empty'), value: 'empty' },
  { title: t('dialogs.vmAdd.copy'), value: 'copy' },
])
const localizedCpuItems = computed(() => itemsCPU.map(item => ({
  ...item,
  title: t('dialogs.vmAdd.cpuCores', { count: item.value }, item.value),
})))

const cloudInitFormDirty = computed(
  () => JSON.stringify(cloudInitForm) !== cloudInitFormSnapshot.value
)
const cloudInitFormError = computed(() => {
  void locale.value
  return formatCloudInitErrors(cloudInitFormErrors.value).join('\n')
})
const cloudInitYamlError = computed(() => {
  void locale.value
  return formatCloudInitErrors(cloudInitYamlErrors.value).join('\n')
})

const postData = reactive<bodyPostVM>({
  type: 'manual',
  projectId: '',
  name: '',
  nodeName: '',
  memoryMegaByte: 8192,
  cpu: 2,
  disks: [
    {
      type: 'empty',
      savePoolUuid: '',
      originalPoolUuid: null,
      originalName: null,
      sizeGigaByte: 32
    }
  ],
  interface: [
    {
      type: 'network',
      mac: null,
      networkUuid: '',
      port: '' as string | null
    }
  ],
  cloudInit: null
})

async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  if (postData.cloudInit) {
    const validation = validateCloudInitYaml(postData.cloudInit.userData)
    if (!validation.ok) {
      cloudInitYamlErrors.value = validation.errors
      cloudInitTab.value = 'yaml'
      return
    }
  }

  loading.value = true
  try {
    const res = await apiClient.POST('/api/tasks/vms', { body: postData })

    if (res.data) {
      notifyTask(res.data[0].uuid)
      dialogState.value = false
    } else if (res.error) {
      notify('error', translationRef('dialogs.vmAdd.failed'), apiErrorRef(res.error))
    }
  } catch {
    notify('error', translationRef('dialogs.vmAdd.failed'), translationRef('dialogs.vmAdd.unreachable'))
  } finally {
    loading.value = false
  }
}

function togleCloudInit(value: unknown) {
  if (value === true) {
    resetCloudInitForm()
    cloudInitTab.value = 'simple'
    cloudInitYamlErrors.value = []
    postData.cloudInit = {
      hostname: '',
      userData: EMPTY_CLOUD_CONFIG
    }
    void loadSavedPublicKeys()
  } else {
    postData.cloudInit = null
  }
}

function resetCloudInitForm() {
  Object.assign(cloudInitForm, createCloudInitFormState())
  cloudInitFormSnapshot.value = JSON.stringify(toRaw(cloudInitForm))
  cloudInitFormErrors.value = []
}

function applyCloudInitForm() {
  if (!postData.cloudInit) {
    return
  }

  const result = mergeCloudInitForm(postData.cloudInit.userData, toRaw(cloudInitForm))
  if (!result.ok) {
    cloudInitFormErrors.value = result.errors
    return
  }

  postData.cloudInit.userData = result.value
  cloudInitFormSnapshot.value = JSON.stringify(toRaw(cloudInitForm))
  cloudInitFormErrors.value = []
  cloudInitYamlErrors.value = []
  cloudInitTab.value = 'yaml'
}

function updateCloudInitUserData(value: unknown) {
  if (!postData.cloudInit) {
    return
  }

  postData.cloudInit.userData = typeof value === 'string' ? value : ''
  cloudInitYamlErrors.value = []
}

async function loadSavedPublicKeys() {
  if (savedPublicKeysLoadAttempted.value) {
    return
  }

  savedPublicKeysLoadAttempted.value = true
  savedPublicKeysLoading.value = true
  savedPublicKeysError.value = false

  try {
    const username = useAuthStore().username
    if (!username) {
      savedPublicKeys.value = []
      return
    }

    const response = await apiClient.GET('/api/users', {
      params: {
        query: {
          nameLike: username,
          limit: 0,
          page: 0,
        },
      },
    })
    const currentUser = response.data?.data.find(user => user.username === username)

    if (!response.data) {
      savedPublicKeysError.value = true
    }
    savedPublicKeys.value = currentUser?.publickeys ?? []
  } catch {
    savedPublicKeys.value = []
    savedPublicKeysError.value = true
  } finally {
    savedPublicKeysLoading.value = false
  }
}

function itemsPort(networkUuid: string) {
  const net = itemsNetworks.value.data
    .filter(n => n.nodeName === postData.nodeName && n.uuid === networkUuid)

  if (net[0]) {
    return net[0].portgroups.map(p => ({ title: p.name, value: p.name }))
  } else {
    return []
  }
}

function addInterface() {
  postData.interface.push({
    type: 'network',
    mac: null,
    networkUuid: '',
    port: null
  });
}
function deleteInterface(index: number) {
  postData.interface.splice(index, 1);
}

let projectResourceRequest = 0

function resetProjectResources() {
  postData.nodeName = ''
  for (const disk of postData.disks) {
    disk.savePoolUuid = ''
    disk.originalPoolUuid = null
    disk.originalName = null
  }
  for (const nic of postData.interface) {
    nic.networkUuid = ''
    nic.port = null
  }
  itemsNodes.value = initNodeList
  itemsNetworks.value = initNetworkList
  itemsStorages.value = initStorageList
  itemsImages.value = initImageList
}

async function loadProjectResources(projectId: string) {
  const request = ++projectResourceRequest
  resetProjectResources()
  if (!projectId) return

  resourcesLoading.value = true
  const queryImage: typeListImageQuery = {
    admin: false,
    limit: 999999,
    page: 1,
    projectId,
  }
  const queryNetwork: typeListNetworkQuery = {
    admin: false,
    limit: 999999,
    page: 1,
    projectId,
  }
  const queryStorage: typeListStorageQuery = {
    admin: false,
    limit: 999999,
    page: 1,
    projectId,
  }

  try {
    const [nodes, networks, storages, images] = await Promise.all([
      getNode(projectId),
      getNetworkList(queryNetwork),
      getStorageList(queryStorage),
      getImageList(queryImage),
    ])
    if (request !== projectResourceRequest) return
    itemsNodes.value = nodes
    itemsNetworks.value = networks
    itemsStorages.value = storages
    itemsImages.value = images
  } finally {
    if (request === projectResourceRequest) resourcesLoading.value = false
  }
}

watch(() => postData.projectId, projectId => {
  void loadProjectResources(projectId)
})

onMounted(async () => {
  projectsLoading.value = true
  try {
    const response = await getProjectList({ limit: 0, page: 1 })
    itemsProjects.value = response.data
    if (response.data.length === 1) postData.projectId = response.data[0].id
  } finally {
    projectsLoading.value = false
  }
})


function checkOVS(networkUuid: string): boolean {
  const net = itemsNetworks.value.data
    .filter(n => n.nodeName === postData.nodeName && n.uuid === networkUuid)

  return net.length === 1 && net[0].type === 'openvswitch'
}
</script>

<style scoped>
.vm-create-dialog__form {
  width: 100%;
  max-height: calc(100vh - 32px);
}

.vm-create-dialog {
  display: flex;
  max-height: inherit;
  flex-direction: column;
}

.vm-create-dialog__body {
  overflow-y: auto;
}

.vm-create-dialog__section + .vm-create-dialog__section {
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.vm-create-dialog__section-title {
  margin-bottom: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
</style>
