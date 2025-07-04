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
          <v-row v-for="disk in postData.disks">
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
          <v-checkbox density="comfortable" @update:model-value="togleCloudInit" label="Use cloud-init"
            color="primary"></v-checkbox>
          <div v-if="postData.cloudInit">
            <v-text-field variant="outlined" density="comfortable" v-model="postData.cloudInit.hostname"
              label="Host name" dense :rules="[r.required, r.limitLength64, r.characterRestrictions]">
            </v-text-field>
            <v-textarea variant="outlined" density="comfortable" clearable class="text-caption" auto-grow
              v-model="postData.cloudInit.userData" clear-icon="mdi-close-circle" label="User-data"></v-textarea>
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


const useCloudInit = ref(true)

const loading = ref(false)
const dialogState = defineModel({ default: false })

const itemsNodes = ref<typeListNode>(initNodeList)
const itemsNetworks = ref<typeListNetwork>(initNetworkList)
const itemsStorages = ref<schemas['StoragePage']>(initStorageList)
const itemsImages = ref<typeListImage>(initImageList)

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

function togleCloudInit(value: any) {
  if (value) {
    postData.cloudInit = {
      hostname: '',
      userData: `#cloud-config
password: password
chpasswd: {expire: False}
ssh_pwauth: True
ssh_authorized_keys:
  - ssh-rsa AAA...fHQ== sample@example.com
          `
    }
  } else {
    postData.cloudInit = null
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
