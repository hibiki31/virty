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
                counter="64" @change="(val: string) => postData.cloudInit.hostname = val"></v-text-field>
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
          <v-row v-for="disk in postData.disks" :key="disk.id">
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
                item-text="name" item-value="uuid" v-model="disk.savePoolUuid"></v-select>
            </v-col>
            <v-col cols="12" md="2" v-if="disk.type === 'copy'">
              <v-select variant="outlined" density="comfortable" label="Src Pool"
                :items="itemsStorages.data.filter(x => x.nodeName === postData.nodeName)"
                v-model="disk.originalPoolUuid" :rules="[r.required]" item-text="name" item-value="uuid"></v-select>
            </v-col>
            <v-col cols="12" md="3" v-if="disk.type === 'copy'">
              <v-select variant="outlined" density="comfortable" label="Src Image"
                :items="itemsImages.data.filter(x => x.storageUuid === disk.originalPoolUuid)" :rules="[r.required]"
                item-text="name" item-value="name" v-model="disk.originalName"></v-select>
            </v-col>
          </v-row>
          <v-divider class="pt-5"></v-divider>
          <!-- ネットワーク -->
          <v-row v-for="(nic, index) in postData.interface" :key="index">
            <v-col cols="12" md="3">
              <v-select :items="[{ text: 'Network', value: 'network' }]" :rules="[r.required]" v-model="nic.type"
                label="Network Type"></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select :items="itemsNetworks.data.filter(x => x.nodeName === postData.nodeName)" item-text="name"
                item-value="name" :rules="[r.required]" v-model="nic.networkName" label="Network"
                @change="getNetworkDetail()"></v-select>
            </v-col>
            <!-- <v-col cols="12" md="3" v-if="checkOVS(nic.networkName)">
          <v-select :loading="nic.selectPort === null" :items="nic.selectPort" item-text="name" item-value=""
            :rules="[r.required]" v-model="nic.port" label="Port"></v-select>
        </v-col> -->
            <v-col><v-icon class="mt-5" @click="deleteInterface(index)">mdi-minus</v-icon></v-col>
          </v-row>
          <div>
            <v-icon class="ma-1 mb-3" @click="addInterface">mdi-plus</v-icon>
          </div>
        </v-form>


        <v-form class="form-box" ref="step4Form">
          <v-switch dense v-model="useCloudInit" label="Use cloud-init" class="ma-2"></v-switch>
          <div v-if="useCloudInit">
            <v-text-field v-model="postData.cloudInit.hostname" label="Host name" dense
              :rules="[r.required, r.limitLength64, r.characterRestrictions]">
            </v-text-field>
            <v-textarea clearable class="text-caption" outlined auto-grow v-model="postData.cloudInit.userData"
              clear-icon="mdi-close-circle" label="User-data"></v-textarea>
            <v-textarea class="text-caption" outlined clearable auto-grow v-model="postData.cloudInit.networkConfig"
              clear-icon="mdi-close-circle" label="Network-config"></v-textarea>
          </div>
        </v-form>
        <div class="form-box text-caption">
        </div>
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

const useCloudInit = ref(true)

const dialogState = defineModel({ default: false })

const itemsNodes = ref<typeListNode>(initNodeList)
const itemsNetworks = ref<typeListNetwork>(initNetworkList)
const itemsStorages = ref<typeListStorage>(initStorageList)
const itemsImages = ref<typeListImage>(initImageList)

const postData = ref({
  type: 'manual',
  name: '',
  nodeName: '',
  memoryMegaByte: null,
  cpu: null,
  disks: [
    {
      id: 1,
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
      networkName: '',
      selectPort: null
    }
  ],
  cloudInit: {
    hostname: '',
    userData: `#cloud-config
password: password
chpasswd: {expire: False}
ssh_pwauth: True
ssh_authorized_keys:
  - ssh-rsa AAA...fHQ== sample@example.com
          `,
    networkConfig: 'network:\n  version: 2\n  ethernets: []'
  }
})

function submit() {

}

function getNetworkDetail() {
  //       axios.get('/api/networks/' + uuid).then((response) => (nic.selectPort = response.data.portgroups));
}

function addInterface() {
  postData.value.interface.push({
    type: 'network',
    mac: null,
    networkName: '',
    selectPort: null
  });
}
function deleteInterface(index: number) {
  postData.value.interface.splice(index, 1);
}

onMounted(async () => {
  itemsNodes.value = await getNode()
  itemsNetworks.value = await getNetworkList()
  itemsStorages.value = await getStorageList()
})


// export default {
//   name: 'NodeAddDialog',
//   data: function () {
//     return {
//       itemsStorages: [],
//       itemsNetworks: [],
//       itemsImages: [],
//       itemsNodes: [],
//       networkDetail: [],
//       itemsMemory: [
//         { text: '512MB', value: '512' },
//         { text: '1GB', value: '1024' },
//         { text: '2GB', value: '2048' },
//         { text: '4GB', value: '4096' },
//         { text: '8GB', value: '8192' },
//         { text: '16GB', value: '16384' },
//         { text: '32GB', value: '32768' }
//       ],

//       itemsCpu: [
//         { text: '1 Core', value: '1' },
//         { text: '2 Core', value: '2' },
//         { text: '4 Core', value: '4' },
//         { text: '8 Core', value: '8' },
//         { text: '12 Core', value: '12' },
//         { text: '16 Core', value: '16' },
//         { text: '24 Core', value: '24' }
//       ],
//       stepCount: 1,
//       useCloudInit: false,

//       dialogState: false
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
//     addInterface() {
//       this.postData.interface.push({
//         type: 'network',
//         mac: null,
//         networkName: '',
//         selectPort: null
//       });
//     },
//     deleteInterface(index) {
//       this.postData.interface.splice(index, 1);
//     },
//     validateStep1() {
//       if (!this.$refs.step1Form.validate()) {
//         return;
//       }
//       this.stepCount = 2;
//     },
//     validateStep2() {
//       if (!this.$refs.step2Form.validate()) {
//         return;
//       }
//       this.stepCount = 3;
//     },
//     validateStep3() {
//       if (!this.$refs.step3Form.validate()) {
//         return;
//       }
//       this.stepCount = 4;
//     },
//     validateStep4() {
//       if (!this.$refs.step4Form.validate()) {
//         return;
//       }
//       this.stepCount = 5;
//     },
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
//   mounted: function () {
//     axios.get('/api/storages').then((response) => (this.itemsStorages = response.data));
//     axios.get('/api/images').then((response) => (this.itemsImages = response.data));
//     axios.get('/api/networks').then((response) => (this.itemsNetworks = response.data));
//     axios.get('/api/nodes').then((response) => (this.itemsNodes = response.data));
//   }
// };
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
