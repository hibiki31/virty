<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="networkAddForm">
          <v-card-title>Register Netwrok</v-card-title>
          <v-card-text>
            You can register a bridge that has already been created on the host.
            For example, Linux-bridge or OVS-bridge.
            <v-text-field
              v-model="postData.name"
              label="Display name on virty"
              :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
              counter="64"
            ></v-text-field>
            <v-select
              :items="[ { name: 'Linux bridge', value: 'bridge' }, { name: 'Open vSwitch', value: 'ovs' } ]"
              item-text="name"
              item-value="value"
              v-model="postData.type"
              label="Type"
              :rules="[required]"
            >
            </v-select>
            <v-select
              :items="itemsNodes"
              item-text="name"
              item-value="name"
              v-model="postData.nodeName"
              label="Select node name"
              :rules="[required]"
            >
              <template v-slot:item="{ item }">
                <span>{{ item.name }} - {{ item.domain }}</span>
              </template>
              <template v-slot:selection="{ item }">
                <span>{{ item.name }} - {{ item.domain }}</span>
              </template>
            </v-select>
            <v-text-field
              v-model="postData.bridgeDevice"
              label="Bridge Name"
              :rules="[$required]"
              counter="128"
            ></v-text-field>

          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">ADD</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'networkAddDialog',
  data: function() {
    return {
      itemsNodes: [],
      postData: {
        name: '',
        bridgeDevice: '',
        type: 'bridge',
        nodeName: ''
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.networkAddForm.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/networks',
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
    axios.get('/api/nodes').then((response) => (this.itemsNodes = response.data));
  }
};
</script>
