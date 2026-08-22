<template>
  <v-dialog v-model="dialogState" width="calc(100% - 32px)" max-width="1100">
    <v-form class="vm-create-dialog__form" @submit.prevent="submit">
      <v-card class="vm-create-dialog">
        <v-card-title class="d-flex align-center px-4 py-3">
          <span class="text-h6">Create VM</span>
          <v-btn class="ml-auto" icon="mdi-close" size="small" variant="text" aria-label="Close"
            @click="dialogState = false"></v-btn>
        </v-card-title>
        <v-divider></v-divider>

        <v-card-text class="vm-create-dialog__body pa-4">
          <section class="vm-create-dialog__section">
            <h3 class="vm-create-dialog__section-title">Basic</h3>
            <v-row class="ma-n1">
              <v-col cols="12" md="5" class="pa-1">
                <v-text-field v-model="postData.name" variant="outlined" density="compact" label="Name"
                  hide-details="auto"
                  :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                  @change="() => { if (postData.cloudInit) { postData.cloudInit.hostname = postData.name } }"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="3" class="pa-1">
                <v-select v-model="postData.nodeName" variant="outlined" density="compact" label="Node"
                  hide-details="auto" :items="itemsNodes.data" :rules="[r.required]" item-title="name"
                  item-value="name"></v-select>
              </v-col>
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-select v-model="postData.memoryMegaByte" variant="outlined" density="compact" label="Memory"
                  hide-details="auto" :items="itemsMemory" item-title="title" item-value="value"
                  :rules="[r.required]"></v-select>
              </v-col>
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-select v-model="postData.cpu" variant="outlined" density="compact" label="CPU"
                  hide-details="auto" :items="itemsCPU" :rules="[r.required]"></v-select>
              </v-col>
            </v-row>
          </section>

          <section class="vm-create-dialog__section">
            <div class="d-flex align-center ga-3 mb-2">
              <h3 class="vm-create-dialog__section-title mb-0">Storage</h3>
              <span v-if="postData.disks[0]?.type === 'empty'" class="text-caption text-medium-emphasis">
                Attach an ISO from the VM details page after creation.
              </span>
            </div>
            <v-row v-for="(disk, index) in postData.disks" :key="index" class="ma-n1">
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-select v-model="disk.type" variant="outlined" density="compact" label="Mode" hide-details="auto"
                  :items="[{ title: 'Empty', value: 'empty' }, { title: 'Copy', value: 'copy' }]"
                  :rules="[r.required]"></v-select>
              </v-col>
              <v-col cols="6" sm="3" md="2" class="pa-1">
                <v-text-field v-model="disk.sizeGigaByte" variant="outlined" density="compact" label="Size [GB]"
                  hide-details="auto" :rules="[r.required]"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" :md="disk.type === 'copy' ? 3 : 8" class="pa-1">
                <v-select v-model="disk.savePoolUuid" variant="outlined" density="compact" label="Destination pool"
                  hide-details="auto" :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)"
                  :rules="[r.required]" item-title="name" item-value="uuid"></v-select>
              </v-col>
              <v-col v-if="disk.type === 'copy'" cols="12" sm="6" md="2" class="pa-1">
                <v-select v-model="disk.originalPoolUuid" variant="outlined" density="compact" label="Source pool"
                  hide-details="auto" :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)"
                  :rules="[r.required]" item-title="name" item-value="uuid"></v-select>
              </v-col>
              <v-col v-if="disk.type === 'copy'" cols="12" sm="6" md="3" class="pa-1">
                <v-select v-model="disk.originalName" variant="outlined" density="compact" label="Source image"
                  hide-details="auto" :items="itemsImages.data.filter(x => x.storageUuid === disk.originalPoolUuid)"
                  :rules="[r.required]" item-title="name" item-value="name"></v-select>
              </v-col>
            </v-row>
          </section>

          <section class="vm-create-dialog__section">
            <div class="d-flex align-center mb-2">
              <h3 class="vm-create-dialog__section-title mb-0">Network</h3>
              <v-btn class="ml-auto" prepend-icon="mdi-plus" size="small" variant="text"
                @click="addInterface">Add interface</v-btn>
            </div>
            <v-row v-for="(nic, index) in postData.interface" :key="index" class="ma-n1 align-center">
              <v-col cols="10" :md="checkOVS(nic.networkUuid) ? 6 : 11" class="pa-1">
                <v-select v-model="nic.networkUuid" variant="outlined" density="compact" label="Network"
                  hide-details="auto" :items="itemsNetworks.data.filter(x => x.nodeName === postData.nodeName)"
                  item-title="name" item-value="uuid" :rules="[r.required]"></v-select>
              </v-col>
              <v-col v-if="checkOVS(nic.networkUuid)" cols="10" md="5" class="pa-1">
                <v-select v-model="nic.port" variant="outlined" density="compact" label="Port" hide-details="auto"
                  :items="itemsPort(nic.networkUuid)" item-title="name" item-value="value"
                  :rules="[r.required]"></v-select>
              </v-col>
              <v-col cols="2" md="1" class="pa-1 text-right">
                <v-btn icon="mdi-delete-outline" size="small" variant="text" aria-label="Remove interface"
                  @click="deleteInterface(index)"></v-btn>
              </v-col>
            </v-row>
          </section>

          <section class="vm-create-dialog__section">
            <div class="d-flex align-center">
              <h3 class="vm-create-dialog__section-title mb-0">Cloud-init</h3>
              <v-checkbox data-testid="cloud-init-toggle" class="ml-auto flex-grow-0" density="compact" hide-details
                :model-value="postData.cloudInit !== null" label="Enable" color="primary"
                @update:model-value="togleCloudInit"></v-checkbox>
            </div>

            <div v-if="postData.cloudInit" class="mt-2">
              <v-row class="ma-n1 align-center">
                <v-col cols="12" md="7" class="pa-1">
                  <v-text-field v-model="postData.cloudInit.hostname" variant="outlined" density="compact"
                    label="Host name" hide-details="auto"
                    :rules="[r.required, r.limitLength64, r.characterRestrictions]"></v-text-field>
                </v-col>
                <v-col cols="12" md="5" class="pa-1">
                  <v-tabs data-testid="cloud-init-tabs" v-model="cloudInitTab" density="compact" color="primary"
                    grow>
                    <v-tab value="simple" @click="cloudInitTab = 'simple'">Simple form</v-tab>
                    <v-tab value="yaml" @click="cloudInitTab = 'yaml'">YAML</v-tab>
                  </v-tabs>
                </v-col>
              </v-row>

              <v-window v-model="cloudInitTab">
                <v-window-item value="simple">
                  <v-alert class="my-2 py-2" density="compact" type="warning" variant="tonal">
                    Passwords remain in task history and the cloud-init ISO; initial scripts run once as root.
                    Prefer SSH key authentication.
                  </v-alert>

                  <v-row class="ma-n1">
                    <v-col cols="12" md="6" class="pa-1">
                      <v-text-field data-testid="cloud-init-username" v-model="cloudInitForm.username"
                        variant="outlined" density="compact" label="Initial user name" hide-details="auto"
                        hint="Leave blank to use the image default"></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-text-field data-testid="cloud-init-password" v-model="cloudInitForm.password"
                        variant="outlined" density="compact" label="Password" hide-details="auto" type="password"
                        autocomplete="new-password"></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-checkbox data-testid="cloud-init-password-expires" v-model="cloudInitForm.passwordExpires"
                        density="compact" hide-details label="Require password change on first login"
                        color="primary"></v-checkbox>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-checkbox data-testid="cloud-init-ssh-password-authentication"
                        v-model="cloudInitForm.sshPasswordAuthentication" density="compact" hide-details
                        label="Enable SSH password authentication" color="primary"></v-checkbox>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-select data-testid="cloud-init-saved-public-keys" v-model="cloudInitForm.selectedPublicKeys"
                        variant="outlined" density="compact" label="Saved SSH public keys" hide-details="auto"
                        :items="savedPublicKeys" item-title="name" item-value="publickey" multiple chips closable-chips
                        :loading="savedPublicKeysLoading" no-data-text="No saved SSH public keys"></v-select>
                    </v-col>
                    <v-col cols="12" md="6" class="pa-1">
                      <v-textarea data-testid="cloud-init-manual-public-keys" v-model="cloudInitForm.manualPublicKeys"
                        variant="outlined" density="compact" label="Additional SSH public keys" hide-details="auto"
                        hint="One public key per line" rows="2" auto-grow max-rows="4"></v-textarea>
                    </v-col>
                    <v-col cols="12" class="pa-1">
                      <v-textarea data-testid="cloud-init-script" v-model="cloudInitForm.script" variant="outlined"
                        density="compact" label="Initial script" hide-details="auto" rows="2" auto-grow
                        max-rows="5"></v-textarea>
                    </v-col>
                  </v-row>

                  <v-alert v-if="savedPublicKeysError" data-testid="saved-public-keys-error" class="mt-2 py-2"
                    density="compact" type="warning" variant="tonal">{{ savedPublicKeysError }}</v-alert>
                  <v-alert v-if="cloudInitFormDirty" data-testid="cloud-init-dirty-warning" class="mt-2 py-2"
                    density="compact" type="warning" variant="tonal">
                    Unapplied simple form changes are not sent. CREATE uses the current raw YAML.
                  </v-alert>
                  <v-alert v-if="cloudInitFormError" data-testid="cloud-init-form-error" class="mt-2 py-2"
                    density="compact" type="error" variant="tonal" style="white-space: pre-line">
                    {{ cloudInitFormError }}
                  </v-alert>
                  <div class="text-right mt-2">
                    <v-btn data-testid="cloud-init-apply" color="primary" size="small" variant="tonal"
                      @click="applyCloudInitForm">Apply to YAML</v-btn>
                  </div>
                </v-window-item>

                <v-window-item value="yaml">
                  <v-textarea data-testid="cloud-init-yaml" class="text-caption mt-2" variant="outlined"
                    density="compact" clearable rows="10" :model-value="postData.cloudInit.userData"
                    clear-icon="mdi-close-circle" label="User-data" :error-messages="cloudInitYamlError"
                    style="white-space: pre-line" @update:model-value="updateCloudInitUserData"></v-textarea>
                </v-window-item>
              </v-window>
            </div>
          </section>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions class="justify-end px-4 py-2">
          <v-btn variant="text" @click="dialogState = false">Cancel</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script lang="ts" setup>

import { computed, onMounted, reactive, ref, toRaw } from 'vue';
import r from '@/composables/rules';
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
import { notifyTask } from '@/composables/notify';
import type { schemas } from '@/composables/schemas';
import { asyncSleep } from '@/composables/sleep';
import {
  EMPTY_CLOUD_CONFIG,
  createCloudInitFormState,
  mergeCloudInitForm,
  validateCloudInitYaml,
} from '@/composables/cloudInit';
import type { CloudInitFormState } from '@/composables/cloudInit';
import { useAuthStore } from '@/stores/auth';


const loading = ref(false)
const dialogState = defineModel({ default: false })

const itemsNodes = ref<typeListNode>(initNodeList)
const itemsNetworks = ref<typeListNetwork>(initNetworkList)
const itemsStorages = ref<schemas['StoragePage']>(initStorageList)
const itemsImages = ref<typeListImage>(initImageList)
const cloudInitTab = ref<'simple' | 'yaml'>('simple')
const cloudInitForm = reactive<CloudInitFormState>(createCloudInitFormState())
const cloudInitFormSnapshot = ref(JSON.stringify(toRaw(cloudInitForm)))
const cloudInitFormError = ref('')
const cloudInitYamlError = ref('')
const savedPublicKeys = ref<schemas['UserPublickey'][]>([])
const savedPublicKeysLoading = ref(false)
const savedPublicKeysError = ref('')
const savedPublicKeysLoadAttempted = ref(false)

const cloudInitFormDirty = computed(
  () => JSON.stringify(cloudInitForm) !== cloudInitFormSnapshot.value
)

const postData = reactive<bodyPostVM>({
  type: 'manual',
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
      cloudInitYamlError.value = validation.errors.join('\n')
      cloudInitTab.value = 'yaml'
      return
    }
  }

  const res = await apiClient.POST('/api/tasks/vms', { body: postData })

  if (res.data) {
    notifyTask(res.data[0].uuid)
    dialogState.value = false
  }

  asyncSleep(500)
  if (res.data) {
    notifyTask(res.data[0].uuid)
    dialogState.value = false
  }
  loading.value = false
}

function togleCloudInit(value: unknown) {
  if (value === true) {
    resetCloudInitForm()
    cloudInitTab.value = 'simple'
    cloudInitYamlError.value = ''
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
  cloudInitFormError.value = ''
}

function applyCloudInitForm() {
  if (!postData.cloudInit) {
    return
  }

  const result = mergeCloudInitForm(postData.cloudInit.userData, toRaw(cloudInitForm))
  if (!result.ok) {
    cloudInitFormError.value = result.errors.join('\n')
    return
  }

  postData.cloudInit.userData = result.value
  cloudInitFormSnapshot.value = JSON.stringify(toRaw(cloudInitForm))
  cloudInitFormError.value = ''
  cloudInitYamlError.value = ''
  cloudInitTab.value = 'yaml'
}

function updateCloudInitUserData(value: unknown) {
  if (!postData.cloudInit) {
    return
  }

  postData.cloudInit.userData = typeof value === 'string' ? value : ''
  cloudInitYamlError.value = ''
}

async function loadSavedPublicKeys() {
  if (savedPublicKeysLoadAttempted.value) {
    return
  }

  savedPublicKeysLoadAttempted.value = true
  savedPublicKeysLoading.value = true
  savedPublicKeysError.value = ''

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
      savedPublicKeysError.value = 'Saved SSH public keys could not be loaded. You can enter keys manually.'
    }
    savedPublicKeys.value = currentUser?.publickeys ?? []
  } catch {
    savedPublicKeys.value = []
    savedPublicKeysError.value = 'Saved SSH public keys could not be loaded. You can enter keys manually.'
  } finally {
    savedPublicKeysLoading.value = false
  }
}

function itemsPort(networkUuid: string) {
  const net = itemsNetworks.value.data
    .filter(n => n.nodeName === postData.nodeName && n.uuid === networkUuid)

  if (net[0]) {
    return net[0].portgroups.map(p => ({ title: p.name, value: p.vlanId }))
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

onMounted(async () => {
  const queryImage: typeListImageQuery = {
    admin: true,
    limit: 999999,
    page: 1,
  }
  const queryNetwork: typeListNetworkQuery = {
    admin: true,
    limit: 999999,
    page: 1,
  }
  const queryStorage: typeListStorageQuery = {
    admin: true,
    limit: 999999,
    page: 1,
  }

  itemsNodes.value = await getNode()
  itemsNetworks.value = await getNetworkList(queryNetwork)
  itemsStorages.value = await getStorageList(queryStorage)
  itemsImages.value = await getImageList(queryImage)
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
