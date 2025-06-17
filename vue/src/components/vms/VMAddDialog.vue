<template>
  <v-dialog width="900" v-model="dialogState" color="black">
    <v-card title="Create VM">
      <v-card-text>
        <v-form class="form-box">
          <!-- 基本 -->
          <v-row cols="12">
            <v-col>
              <v-text-field variant="outlined" density="comfortable" label="Name" v-model="postData.name"
                :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                counter="64"
                @change="() => { if (postData.cloudInit) { postData.cloudInit.hostname = postData.name } }"></v-text-field>
            </v-col>
            <v-col md="2">
              <v-select variant="outlined" density="comfortable" label="Memory" :items="itemsMemory"
                :rules="[r.required]" v-model="postData.memoryMegaByte"></v-select>
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
          </v-row>
          <v-divider class="pt-5"></v-divider>
          <!-- ネットワーク -->
          <v-row v-for="(nic, index) in postData.interface" :key="index">
            <v-col cols="12" md="3">
              <v-select variant="outlined" density="comfortable" :items="[{ title: 'Network', value: 'network' }]"
                :rules="[r.required]" v-model="nic.type" label="Network Type"></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select variant="outlined" density="comfortable"
                :items="itemsNetworks.data.filter(x => x.nodeName === postData.nodeName)" item-title="name"
                item-value="uuid" :rules="[r.required]" v-model="nic.networkUuid" label="Network"
                @change="getNetworkDetail()"></v-select>
            </v-col>
            <v-col cols="12" md="3" v-if="checkOVS(nic.networkUuid)">
              <v-select :loading="nic.port === null" :items="[]" item-title="name" item-value="" :rules="[r.required]"
                label="Port"></v-select>
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
        </v-form>
      </v-card-text>
      <v-divider></v-divider>

      <v-card-actions>
        <v-btn color="primary" class="mr-2" @click="submit">CREATE</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</template>

<script lang="ts" setup>
import { ref, defineModel, onMounted } from 'vue';
import * as r from '@/composables/rules';

import { itemsCPU, itemsMemory } from '@/composables/vm'
import type { typeListNode } from '@/composables/nodes';
import { initNodeList, getNode } from '@/composables/nodes';

import type { typeListNetwork } from '@/composables/network';
import { initNetworkList, getNetworkList } from '@/composables/network';

import type { typeListStorage } from '@/composables/storage';
import { initStorageList, getStorageList } from '@/composables/storage';

import type { typeListImage } from '@/composables/image';
import { initImageList, getImageList } from '@/composables/image';
import { apiClient } from '@/api';
import { notifyTask } from '@/composables/notify';
import type { bodyPostVM } from '@/composables/vm';

const useCloudInit = ref(true)

const dialogState = defineModel({ default: false })

const itemsNodes = ref<typeListNode>(initNodeList)
const itemsNetworks = ref<typeListNetwork>(initNetworkList)
const itemsStorages = ref<typeListStorage>(initStorageList)
const itemsImages = ref<typeListImage>(initImageList)

const postData = reactive<bodyPostVM>({
  type: 'manual',
  name: '',
  nodeName: '',
  memoryMegaByte: 512,
  cpu: 2,
  disks: [
    {
      type: 'empty',
      savePoolUuid: 'default',
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
      port: null
    }
  ],
  cloudInit: null
})

function submit() {

  apiClient.POST('/api/tasks/vms', { body: postData }).then(res => {
    if (res.data) {
      notifyTask(res.data[0].uuid || "")
      dialogState.value = false
    }
  })
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


function getNetworkDetail() {
  //       axios.get('/api/networks/' + uuid).then((response) => (nic.selectPort = response.data.portgroups));
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
  itemsNodes.value = await getNode()
  itemsNetworks.value = await getNetworkList()
  itemsStorages.value = await getStorageList()
  itemsImages.value = await getImageList(99999, 1)
})

function checkOVS(networkName: string) {
  const net = itemsNetworks.value.data.filter(x => x.nodeName === postData.nodeName && x.name === networkName);
  if (net.length === 1) {
    return (net[0].type === 'openvswitch');
  }
}


// export default {
//   name: 'NodeAddDialog',
//   data: function () {
//     return {
//       networkDetail: [],
//     };
//   },
//   methods: {
//     openDialog() {
//       this.dialogState = true;
//     },
//     checkOVS(networkName) {
//       const net = this.itemsNetworks.filter(x => x.nodeName === this.postData.nodeName && x.name === networkName);
//       if (net.length === 1) {
//         return (net[0].type === 'openvswitch');
//       }
//     },
//     returnUUID(networkName) {
//       const net = this.itemsNetworks.filter(x => x.nodeName === this.postData.nodeName && x.name === networkName);
//       if (net.length === 1) {
//         return net[0].uuid;
//       }
//     },
//     getNetworkDetail(uuid, nic) {
//       axios.get('/api/networks/' + uuid).then((response) => (nic.selectPort = response.data.portgroups));
//     },
//
//     runMethod() {
//       if (!this.useCloudInit) {
//         this.postData.cloudInit = null;
//       }
//       axios.request({
//         method: 'post',
//         url: '/api/vms',
//         data: this.postData
//       })
//         .then(res => {
//           this.$_pushNotice('Please wait for task to complete', 'success');
//           this.dialogState = false;
//         })
//         .catch(error => {
//           this.$_pushNotice(error.response.data.detail, 'error');
//         });
//     }
//   },

</script>

<style>
.v-textarea textarea {
  line-height: 1.1rem !important;
  font-family: monospace, serif;
}

.theme--dark.v-stepper {
  background: #1E1E1E !important;
}

.v-stepper__step {
  padding: 15px !important;
}

.v-stepper__header {
  height: 50px !important;
}

.form-box {
  min-height: 300px;
}

.v-stepper__label {
  text-shadow: 0px 0px 0px #1E1E1E !important;
}
</style>
