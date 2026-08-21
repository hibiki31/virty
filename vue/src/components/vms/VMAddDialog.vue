<template>
  <v-dialog width="900" v-model="dialogState" color="black">
    <v-form ref="formRef" @submit.prevent="submit">
      <v-card title="Create VM">
        <v-card-text>
          <!-- 基本 -->
          <v-row cols="12">
            <v-col>
              <v-text-field variant="outlined" density="comfortable" label="Name" v-model="postData.name"
                :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                counter="64"
                @change="() => { if (postData.cloudInit) { postData.cloudInit.hostname = postData.name } }"></v-text-field>
            </v-col>
            <v-col md="2">
              <v-select variant="outlined" density="comfortable" label="Memory" :items="itemsMemory" item-title="title"
                item-value="value" :rules="[r.required]" v-model="postData.memoryMegaByte"></v-select>
            </v-col>
            <v-col md="2">
              <v-select variant="outlined" density="comfortable" label="CPU" :items="itemsCPU" :rules="[r.required]"
                v-model="postData.cpu"></v-select>
            </v-col>
            <v-col md="3">
              <v-select variant="outlined" density="comfortable" label="Node" :items="itemsNodes.data"
                :rules="[r.required]" item-title="name" item-value="name" v-model="postData.nodeName"></v-select>
            </v-col>
          </v-row>
          <v-divider class="pt-5"></v-divider>

          <!-- ストレージ -->
          <v-row v-for="(disk, index) in postData.disks" :key="index">
            <v-col cols="12" md="2">
              <v-select variant="outlined" density="comfortable"
                :items="[{ title: 'Empty', value: 'empty' }, { title: 'Copy', value: 'copy' }]" :rules="[r.required]"
                v-model="disk.type" label="Mode"></v-select>
            </v-col>
            <v-col cols="12" md="2">
              <v-text-field variant="outlined" density="comfortable" label="Size [GB]" v-model="disk.sizeGigaByte"
                :rules="[r.required]"></v-text-field>
            </v-col>
            <v-col cols="12" md="2">
              <v-select variant="outlined" density="comfortable" label="Dest Pool"
                :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)" :rules="[r.required]"
                item-title="name" item-value="uuid" v-model="disk.savePoolUuid"></v-select>
            </v-col>
            <v-col cols="12" md="2" v-if="disk.type === 'copy'">
              <v-select variant="outlined" density="comfortable" label="Src Pool"
                :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)"
                v-model="disk.originalPoolUuid" :rules="[r.required]" item-title="name" item-value="uuid"></v-select>
            </v-col>
            <v-col cols="12" md="3" v-if="disk.type === 'copy'">
              <v-select variant="outlined" density="comfortable" label="Src Image"
                :items="itemsImages.data.filter(x => x.storageUuid === disk.originalPoolUuid)" :rules="[r.required]"
                item-title="name" item-value="name" v-model="disk.originalName"></v-select>
            </v-col>
            <v-col cols="12" md="6" v-if="disk.type === 'empty'">
              <p class="text-body-2">After creating the VM, you can attach the iso to the CDROM on the details page.
              </p>
            </v-col>
          </v-row>
          <v-divider class="pt-5"></v-divider>
          <!-- ネットワーク -->
          <v-row v-for="(nic, index) in postData.interface" :key="index">
            <v-col cols="12" md="3">
              <v-select variant="outlined" density="comfortable" :items="[{ title: 'Network', value: 'network' }]"
                hide-details :rules="[r.required]" v-model="nic.type" label="Network Type"></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select variant="outlined" density="comfortable"
                :items="itemsNetworks.data.filter(x => x.nodeName === postData.nodeName)" item-title="name" hide-details
                item-value="uuid" :rules="[r.required]" v-model="nic.networkUuid" label="Network"></v-select>
            </v-col>
            <v-col cols="12" md="3" v-if="checkOVS(nic.networkUuid)">
              <v-select variant="outlined" density="comfortable" :items="itemsPort(nic.networkUuid)" item-text="name"
                hide-details item-value="" :rules="[r.required]" v-model="nic.port" label="Port"></v-select>
            </v-col>
            <v-col><v-btn variant="text" size="small" class="mt-1" @click="deleteInterface(index)"
                icon="mdi-minus-circle-outline"></v-btn></v-col>
          </v-row>
          <v-btn variant="text" size="small" class="" @click="addInterface" icon="mdi-plus-circle-outline"></v-btn>
          <v-divider></v-divider>

          <!-- Cloud-init -->
          <v-checkbox data-testid="cloud-init-toggle" density="comfortable"
            :model-value="postData.cloudInit !== null" @update:model-value="togleCloudInit"
            label="Use cloud-init" color="primary"></v-checkbox>
          <div v-if="postData.cloudInit">
            <v-text-field variant="outlined" density="comfortable" v-model="postData.cloudInit.hostname"
              label="Host name" dense :rules="[r.required, r.limitLength64, r.characterRestrictions]">
            </v-text-field>

            <v-tabs data-testid="cloud-init-tabs" v-model="cloudInitTab" color="primary">
              <v-tab value="simple" @click="cloudInitTab = 'simple'">Simple form</v-tab>
              <v-tab value="yaml" @click="cloudInitTab = 'yaml'">YAML</v-tab>
            </v-tabs>

            <v-window v-model="cloudInitTab">
              <v-window-item value="simple">
                <v-alert class="my-3" type="warning" variant="tonal">
                  Plaintext passwords are stored in the VM creation task history and cloud-init ISO.
                  SSH key authentication is recommended.
                </v-alert>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field data-testid="cloud-init-username" variant="outlined" density="comfortable"
                      v-model="cloudInitForm.username" label="Initial user name" hint="Leave blank to use the image default"
                      persistent-hint></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field data-testid="cloud-init-password" variant="outlined" density="comfortable"
                      v-model="cloudInitForm.password" label="Password" type="password"
                      autocomplete="new-password"></v-text-field>
                  </v-col>
                </v-row>

                <v-checkbox data-testid="cloud-init-password-expires" density="comfortable"
                  v-model="cloudInitForm.passwordExpires" label="Require password change on first login"
                  color="primary"></v-checkbox>
                <v-checkbox data-testid="cloud-init-ssh-password-authentication" density="comfortable"
                  v-model="cloudInitForm.sshPasswordAuthentication" label="Enable SSH password authentication"
                  color="primary"></v-checkbox>

                <v-select data-testid="cloud-init-saved-public-keys" variant="outlined" density="comfortable"
                  v-model="cloudInitForm.selectedPublicKeys" :items="savedPublicKeys" item-title="name"
                  item-value="publickey" label="Saved SSH public keys" multiple chips closable-chips
                  :loading="savedPublicKeysLoading" no-data-text="No saved SSH public keys"></v-select>
                <v-alert v-if="savedPublicKeysError" data-testid="saved-public-keys-error" class="mb-3" type="warning"
                  variant="tonal">{{ savedPublicKeysError }}</v-alert>
                <v-textarea data-testid="cloud-init-manual-public-keys" variant="outlined" density="comfortable"
                  v-model="cloudInitForm.manualPublicKeys" auto-grow label="Additional SSH public keys"
                  hint="Enter one public key per line" persistent-hint></v-textarea>

                <v-checkbox data-testid="cloud-init-package-update" density="comfortable"
                  v-model="cloudInitForm.packageUpdate" label="Update package metadata" color="primary"></v-checkbox>
                <v-textarea data-testid="cloud-init-packages" variant="outlined" density="comfortable"
                  v-model="cloudInitForm.packages" auto-grow label="Packages"
                  hint="Enter one package per line" persistent-hint></v-textarea>

                <v-textarea data-testid="cloud-init-script" variant="outlined" density="comfortable"
                  v-model="cloudInitForm.script" auto-grow label="Initial script"></v-textarea>
                <v-alert class="mb-3" type="warning" variant="tonal">
                  The script runs as root once during the cloud-init final stage.
                </v-alert>

                <v-alert v-if="cloudInitFormDirty" data-testid="cloud-init-dirty-warning" class="mb-3" type="warning"
                  variant="tonal">
                  Unapplied simple form changes are not sent. CREATE uses the current raw YAML.
                </v-alert>
                <v-alert v-if="cloudInitFormError" data-testid="cloud-init-form-error" class="mb-3" type="error"
                  variant="tonal" style="white-space: pre-line">{{ cloudInitFormError }}</v-alert>
                <v-btn data-testid="cloud-init-apply" color="primary" variant="tonal" @click="applyCloudInitForm">
                  Apply to YAML
                </v-btn>
              </v-window-item>

              <v-window-item value="yaml">
                <v-textarea data-testid="cloud-init-yaml" variant="outlined" density="comfortable" clearable
                  class="text-caption mt-3" auto-grow :model-value="postData.cloudInit.userData"
                  clear-icon="mdi-close-circle" label="User-data" :error-messages="cloudInitYamlError"
                  style="white-space: pre-line" @update:model-value="updateCloudInitUserData"></v-textarea>
              </v-window-item>
            </v-window>
          </div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="primary" class="mr-2" type="submit" :loading="loading">CREATE</v-btn>
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
