<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="dialogForm">
          <v-card-title>Network Change</v-card-title>
          <v-card-text>
            <v-select
              :loading="itemNetworks === null"
              :items="itemNetworks"
              item-text="name"
              item-value="name"
              :rules="[$required]"
              v-model="sendData.networkName"
              label="Network"
            ></v-select>
            <v-select
              v-if="networkIsOVS"
              :loading="itemPorts === null && sendData.networkName !== ''"
              :items="itemPorts"
              item-text="name"
              item-value="name"
              :rules="[$required]"
              v-model="sendData.port"
              label="Port"
            ></v-select>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn :loading="this.loadingSubmit" color="primary" v-on:click="runMethod">Change</v-btn>
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
      sendData: {
        uuid: '',
        mac: '',
        networkName: '',
        port: null
      },
      itemPorts: null,
      itemNetworks: [],
      loadingSubmit: false,
      networkIsOVS: false,
      dialogState: false,
      isoImages: []
    };
  },
  watch: {
    'sendData.networkName': function(val) {
      this.getNetworkDetail(val);
    }
  },
  methods: {
    openDialog(uuidDomain, macNet, nodeName) {
      this.sendData.uuid = uuidDomain;
      this.sendData.mac = macNet;
      this.dialogState = true;
      axios.get('/api/networks').then((res) => {
        this.itemNetworks = res.data.filter(x => x.nodeName===nodeName);
      });
    },
    getNetworkDetail(networkName) {
      const net = this.itemNetworks.filter(x => x.name === networkName);
      let uuid = null;
      if (net.length === 1) {
        uuid = net[0].uuid;
      }
      axios.get('/api/networks/' + uuid).then((response) => {
        this.itemPorts = response.data.xml.portgroup;
        if (response.data.xml.type === 'openvswitch') {
          this.networkIsOVS = true;
        }
      });
    },
    runMethod() {
      if (!this.$refs.dialogForm.validate()) {
        return;
      }
      this.loadingSubmit = true;
      axios.request({
        method: 'patch',
        url: '/api/vms/network',
        data: this.sendData
      })
        .then(res => {
          this.$_pushNotice('Added a task. Please wait for it to complete.', 'success');
          this.dialogState = false;
          this.loadingSubmit = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  }
};
</script>
