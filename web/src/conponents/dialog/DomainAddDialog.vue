<template>
 <v-dialog width="700" v-model="dialogState">
      <v-card>
        <v-form ref="domainAddforms">
          <v-card-title>Create VM</v-card-title>
          <v-card-text>
            <!-- 名前 -->
            <v-text-field
              v-model="postData.name"
              label="Name"
              :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
              counter="64"
            ></v-text-field>

            <v-row>
              <!-- メモリ -->
              <v-col cols="12" md="6">
                <v-select
                  :items="itemsMemory"
                  :rules="[$required]"
                  v-model="postData.memoryMegaByte"
                  label="Memory"
                ></v-select>
              </v-col>
              <!-- CPU -->
              <v-col cols="12" md="6">
                <v-select
                  :items="itemsCpu"
                  :rules="[$required]"
                  v-model="postData.cpu"
                  label="CPU"
                ></v-select>
              </v-col>
            </v-row>

            <!-- ノード -->
            <v-select
              :items="itemsNodes"
              :rules="[$required]"
              item-text="name"
              item-value="name"
              v-model="postData.nodeName"
              label="Node"
            ></v-select>

            <div v-if="postData.nodeName != ''">
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

            <!-- インターフェイス -->
            <v-row v-for="(nic, index) in postData.interface" :key="index">
              <v-col cols="12" md="5">
                <v-select
                  :items="[{ text: 'Network', value: 'network' }]"
                  :rules="[$required]"
                  v-model="nic.type"
                  label="Network Type"
                ></v-select>
              </v-col>
              <v-col cols="12" md="7">
                <v-select
                  :items="itemsNetworks.filter(x => x.nodeName===postData.nodeName)"
                  item-text="name"
                  item-value="name"
                  :rules="[$required]"
                  v-model="nic.networkName"
                  label="Network"
                ></v-select>
              </v-col>
            </v-row>
            </div>
            <!-- Init -->
            <v-switch
            dense
            v-model="useCloudInit"
            label="Use cloud-init"
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
                v-model="postData.cloudInit.userData"
                clear-icon="mdi-close-circle"
                label="User-data"
              ></v-textarea>
              <v-textarea
                clearable
                dense
                v-model="postData.cloudInit.networkConfig"
                clear-icon="mdi-close-circle"
                label="User-data"
              ></v-textarea>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">CREATE</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
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
            networkName: ''
          }
        ],
        cloudInit: {
          hostname: '',
          userData: '#cloud-config',
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
    runMethod() {
      if (!this.$refs.domainAddforms.validate()) {
        return;
      }
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
