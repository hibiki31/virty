<template>
  <v-dialog width="700" v-model="dialogState" color="black">
    <v-stepper v-model="stepCount">
      <v-stepper-header>
        <v-stepper-step
          :complete="stepCount > 1"
          :rules="[() => true]"
          step="1"
        >
          Spec
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="stepCount > 2"
          step="2"
        >
          Storage
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="stepCount > 3"
          step="3"
        >
          Network
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="stepCount > 4"
          step="4"
        >
          Cloud-init
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="stepCount > 5"
          step="5"
        >
          Confirmation
        </v-stepper-step>
      </v-stepper-header>

      <v-stepper-items>
        <v-stepper-content step="1">
          <v-form class="form-box" ref="step1Form">
            <v-text-field
              v-model="postData.name"
              label="Name"
              :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
              counter="64"
            ></v-text-field>
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  :items="itemsMemory"
                  :rules="[$required]"
                  v-model="postData.memoryMegaByte"
                  label="Memory"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  :items="itemsCpu"
                  :rules="[$required]"
                  v-model="postData.cpu"
                  label="CPU"
                ></v-select>
              </v-col>
            </v-row>
            <v-select
              :items="itemsNodes"
              :rules="[$required]"
              item-text="name"
              item-value="name"
              v-model="postData.nodeName"
              label="Node"
            ></v-select>
          </v-form>
          <v-btn color="primary" @click="validateStep1" class="mr-2">
            Next
          </v-btn>
          <v-btn text @click="dialogState = false">
            Cancel
          </v-btn>
        </v-stepper-content>

        <v-stepper-content step="2">
          <v-form class="form-box" ref="step2Form">
            <v-row v-for="disk in postData.disks" :key="disk.id">
              <v-col cols="12" md="3">
                <v-select
                  :items="[{ text: 'Empty', value: 'empty' }, { text: 'Copy', value: 'copy' }]"
                  :rules="[$required]"
                  v-model="disk.type"
                  label="Storage Type"
                ></v-select>
              </v-col>
              <v-col cols="12" md="2" v-if="disk.type==='empty'">
                <v-text-field
                  v-model="disk.sizeGigaByte"
                  label="Size GB"
                  :rules="[$required]"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3" v-if="disk.type==='copy'">
                <v-select
                  :items="itemsStorages.filter(x => x.nodeName===postData.nodeName)"
                  :rules="[$required]"
                  item-text="name"
                  item-value="uuid"
                  v-model="disk.originalPoolUuid"
                  label="Src Pool"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3" v-if="disk.type==='copy'">
                <v-select
                  :items="itemsImages.filter(x=> x.storageUuid === disk.originalPoolUuid)"
                  :rules="[$required]"
                  item-text="name"
                  item-value="name"
                  v-model="disk.originalName"
                  label="Src Image"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  :items="itemsStorages.filter(x => x.nodeName===postData.nodeName)"
                  :rules="[$required]"
                  item-text="name"
                  item-value="uuid"
                  v-model="disk.savePoolUuid"
                  label="Dest Pool"
                ></v-select>
              </v-col>
            </v-row>
          </v-form>
          <v-btn color="primary" @click="validateStep2" class="mr-2">
            Next
          </v-btn>
          <v-btn text @click="stepCount = 1">
            Back
          </v-btn>
        </v-stepper-content>

        <v-stepper-content step="3">
          <v-form class="form-box" ref="step3Form">
            <v-row v-for="(nic, index) in postData.interface" :key="index">
              <v-col cols="12" md="3">
                <v-select
                  :items="[{ text: 'Network', value: 'network' }]"
                  :rules="[$required]"
                  v-model="nic.type"
                  label="Network Type"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  :items="itemsNetworks.filter(x => x.nodeName===postData.nodeName)"
                  item-text="name"
                  item-value="name"
                  :rules="[$required]"
                  v-model="nic.networkName"
                  label="Network"
                  @change="getNetworkDetail(returnUUID(nic.networkName), nic)"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3" v-if="checkOVS(nic.networkName)">
                <v-select
                  :loading="nic.selectPort === null"
                  :items="nic.selectPort"
                  item-text="name"
                  item-value=""
                  :rules="[$required]"
                  v-model="nic.port"
                  label="Port"
                ></v-select>
              </v-col>
            </v-row>
            <div>
              <v-icon class="ma-1 mb-3" @click="addInterface">mdi-plus</v-icon>
            </div>
          </v-form>
          <v-btn color="primary" @click="validateStep3" class="mr-2">
            Next
          </v-btn>
          <v-btn text @click="stepCount = 2">
            Back
          </v-btn>
        </v-stepper-content>

        <v-stepper-content step="4">
          <v-form class="form-box" ref="step4Form">
            <v-switch
              dense
              v-model="useCloudInit"
              label="Use cloud-init"
              class="ma-2"
            ></v-switch>
            <div v-if="useCloudInit">
              <v-text-field
                v-model="postData.cloudInit.hostname"
                label="Host name"
                dense
                :rules="[$required, $limitLength64, $hostNameCharacter]"
              >
              </v-text-field>
              <v-textarea
                clearable
                class="text-caption"
                outlined
                auto-grow
                v-model="postData.cloudInit.userData"
                clear-icon="mdi-close-circle"
                label="User-data"
              ></v-textarea>
              <v-textarea
                class="text-caption"
                outlined
                clearable
                auto-grow
                v-model="postData.cloudInit.networkConfig"
                clear-icon="mdi-close-circle"
                label="Network-config"
              ></v-textarea>
            </div>
          </v-form>
          <v-btn color="primary" @click="validateStep4" class="mr-2">
            Next
          </v-btn>
          <v-btn text @click="stepCount = 3">
            Back
          </v-btn>
        </v-stepper-content>
        <v-stepper-content step="5">
          <div class="form-box text-caption">
          </div>
          <v-btn color="primary" class="mr-2" @click="runMethod">CREATE</v-btn>
          <v-btn text @click="stepCount = 4">
            Back
          </v-btn>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
  </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NodeAddDialog',
  data: function() {
    return {
      itemsStorages: [],
      itemsNetworks: [],
      itemsImages: [],
      itemsNodes: [],
      networkDetail: [],
      itemsMemory: [
        { text: '512MB', value: '512' },
        { text: '1GB', value: '1024' },
        { text: '2GB', value: '2048' },
        { text: '4GB', value: '4096' },
        { text: '8GB', value: '8192' },
        { text: '16GB', value: '16384' },
        { text: '32GB', value: '32768' }
      ],

      itemsCpu: [
        { text: '1 Core', value: '1' },
        { text: '2 Core', value: '2' },
        { text: '4 Core', value: '4' },
        { text: '8 Core', value: '8' },
        { text: '12 Core', value: '12' },
        { text: '16 Core', value: '16' },
        { text: '24 Core', value: '24' }
      ],
      stepCount: 1,
      useCloudInit: false,
      postData: {
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
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    checkOVS(networkName) {
      const net = this.itemsNetworks.filter(x => x.nodeName===this.postData.nodeName && x.name === networkName);
      if (net.length === 1) {
        return (net[0].type==='openvswitch');
      }
    },
    returnUUID(networkName) {
      const net = this.itemsNetworks.filter(x => x.nodeName===this.postData.nodeName && x.name === networkName);
      if (net.length === 1) {
        return net[0].uuid;
      }
    },
    getNetworkDetail(uuid, nic) {
      axios.get('/api/networks/' + uuid).then((response) => (nic.selectPort = response.data.xml.portgroup));
    },
    addInterface() {
      this.postData.interface.push({
        type: 'network',
        mac: null,
        networkName: '',
        selectPort: null
      });
    },
    validateStep1() {
      if (!this.$refs.step1Form.validate()) {
        return;
      }
      this.stepCount = 2;
    },
    validateStep2() {
      if (!this.$refs.step2Form.validate()) {
        return;
      }
      this.stepCount = 3;
    },
    validateStep3() {
      if (!this.$refs.step3Form.validate()) {
        return;
      }
      this.stepCount = 4;
    },
    validateStep4() {
      if (!this.$refs.step4Form.validate()) {
        return;
      }
      this.stepCount = 5;
    },
    runMethod() {
      if (!this.useCloudInit) {
        this.postData.cloudInit = null;
      }
      axios.request({
        method: 'post',
        url: '/api/vms',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.dialogState = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  },
  mounted: function() {
    axios.get('/api/storages').then((response) => (this.itemsStorages = response.data));
    axios.get('/api/images').then((response) => (this.itemsImages = response.data));
    axios.get('/api/networks').then((response) => (this.itemsNetworks = response.data));
    axios.get('/api/nodes').then((response) => (this.itemsNodes = response.data));
  }
};
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
