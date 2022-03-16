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
            <v-row>
              <v-col cols="12" md="6" lg="6">
                <v-select
                  :items="itemsIssuances"
                  :rules="[$required]"
                  item-text="ticket.name"
                  item-value="id"
                  v-model="postData.issuanceId"
                  @change="changeTicket"
                  label="Ticket"
                ></v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-text-field
                  v-model="postData.name"
                  label="Virtual machine name"
                  :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
                  counter="64"
                  :disabled="postData.issuanceId === null"
                  @change="(val) => postData.cloudInit.hostname = val"
                ></v-text-field>
              </v-col>
                <v-col>
                  <v-checkbox
                    v-model="manualSpec"
                    label="Manual spec"
                  ></v-checkbox>
                </v-col>
            </v-row>
            <v-row v-if="manualSpec">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="postData.core"
                  label="Cores"
                  :rules="[$required, $intValueRestrictions,(val) => (val <= useTicket.core && val > 0) || 'Exceeds available quantity' ]"
                  :counter="useTicket.core"
                  :counter-value="(val) => val"
                  :error="useTicket.core < postData.cores"
                  :disabled="postData.issuanceId === null"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="postData.memory"
                  label="Memory"
                  :rules="[$required, $intValueRestrictions,(val) => (val <= useTicket.memory && val > 0) || 'Exceeds available quantity' ]"
                  :counter="useTicket.memory"
                  :counter-value="(val) => val"
                  :disabled="postData.issuanceId === null"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row v-else>
              <v-col cols="12" md="6">
                <v-select
                  :items="itemsCpu.filter(x => x.value <= useTicket.core)"
                  :rules="[$required]"
                  v-model="postData.core"
                  label="CPU"
                  :disabled="postData.issuanceId === null"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  :items="itemsMemory.filter(x => x.value <= useTicket.memory)"
                  :rules="[$required]"
                  v-model="postData.memory"
                  label="Memory"
                  :disabled="postData.issuanceId === null"
                ></v-select>
              </v-col>
            </v-row>
          </v-form>
          <v-btn color="primary" @click="validateStep1" class="mr-2">
            Next
          </v-btn>
          <v-btn text @click="dialogState = false">
            Cancel
          </v-btn>
        </v-stepper-content>

        <!-- ストレージ -->
        <v-stepper-content step="2">
          <v-form class="form-box" ref="step2Form">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  :items="useTicket.flavors"
                  item-text="name"
                  item-value="id"
                  :rules="[$required]"
                  v-model="postData.flavorId"
                  label="OS"
                >
                <template v-slot:item="{ item }">
                  <v-icon class="pr-2">mdi-ubuntu</v-icon>
                  <span>{{ item.name }}</span>
                </template>
                </v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col lg="6" md="6">
                <v-text-field
                  v-model.number="postData.flavorSizeG"
                  label="Storage Size"
                  :rules="[$required, $intValueRestrictions,(val) => (val > 0) || 'Exceeds available quantity' ]"
                  counter="512"
                  :counter-value="(val) => val"
                  :disabled="postData.issuanceId === null"
                  suffix="GB"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  :items="useTicket.storagePools"
                  item-text="name"
                  item-value="id"
                  :rules="[$required]"
                  v-model="postData.storagePoolId"
                  label="Storage Spec"
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
            <v-row v-for="(nic, index) in postData.interfaces" :key="index">
              <v-col cols="12" md="6">
                <v-select
                  :items="useTicket.networkPools"
                  item-text="name"
                  item-value="id"
                  append-outer-icon="mdi-delete"
                  :rules="[$required]"
                  v-model="nic.id"
                  label="Network"
                  @click:append-outer="deleteInterface(index)"
                ></v-select>
              </v-col>
            </v-row>
            <div>
              <v-icon class="ma-1 mb-3" @click="addInterface">mdi-plus-box</v-icon>
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
                class="pb-1"
                :rules="[$required, $limitLength64, $characterRestrictions]"
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
      useTicket: {
        core: 1,
        flavors: [],
        id: 0,
        isolatedNetworks: 0,
        memory: 512,
        name: ''
      },
      itemsIssuances: [],
      itemsStorages: [],
      itemsNetworks: [],
      itemsImages: [],
      itemsNodes: [],
      networkDetail: [],
      itemsMemory: [
        { text: '512MB', value: 512 },
        { text: '1GB', value: 1024 },
        { text: '2GB', value: 2048 },
        { text: '4GB', value: 4096 },
        { text: '8GB', value: 8192 },
        { text: '16GB', value: 16384 },
        { text: '32GB', value: 32768 }
      ],

      itemsCpu: [
        { text: '1 Core', value: 1 },
        { text: '2 Core', value: 2 },
        { text: '4 Core', value: 4 },
        { text: '8 Core', value: 8 },
        { text: '12 Core', value: 14 },
        { text: '16 Core', value: 16 },
        { text: '24 Core', value: 24 }
      ],
      stepCount: 1,
      useCloudInit: false,
      manualSpec: false,
      postData: {
        type: 'ticket',
        issuanceId: null,
        name: '',
        memory: 1024,
        core: 1,
        flavorId: null,
        flavorSizeG: 16,
        storagePoolId: null,
        interfaces: [
          {
            id: null,
            mac: null
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
    openDialog(useTicket=false) {
      this.useTicket = useTicket;
      this.dialogState = true;
    },
    counterValueInt(value) {
      return value;
    },
    changeTicket() {
      this.useTicket = this.itemsIssuances.filter(x => x.id===this.postData.issuanceId)[0].ticket;
      console.log(JSON.stringify(this.useTicket, null, 3));
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
      axios.get('/api/networks/' + uuid).then((response) => (nic.selectPort = response.data.portgroups));
    },
    addInterface() {
      this.postData.interfaces.push({
        id: null,
        mac: null
      });
    },
    deleteInterface(index) {
      this.postData.interface.splice(index, 1);
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
        url: '/api/vms/ticket',
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
    axios.get('/api/tickets/issuances').then((response) => (this.itemsIssuances = response.data));
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
