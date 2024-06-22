<template>
 <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>Add Port</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="sendData.name"
            label="Name"
            :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
            counter="64"
          ></v-text-field>
          <v-text-field
            v-model="sendData.vlanId"
            label="VLAN ID"
            :rules="[$required, validateVLANID]"
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
  name: 'networkPortAdd',
  data: function() {
    return {
      itemsNodes: [],
      sendData: {
        uuid: '',
        name: '',
        vlanId: '',
        default: false
      },
      data: {},
      dialogState: false
    };
  },
  methods: {
    openDialog(data) {
      this.dialogState = true;
      this.data = data;
      this.sendData.uuid = data.uuid;
    },
    runMethod() {
      if (!this.$refs.dialogForm.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/networks/ovs',
        data: this.sendData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.dialogState = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    },
    validateVLANID(value) {
      if (isNaN(value)) {
        return false || 'number onry';
      }
      return (Number(value) > 0 && Number(value) < 4095) || '1 ~ 4095';
    }
  },
  mounted: function() {
    axios.get('/api/nodes').then((response) => (this.itemsNodes = response.data));
  }
};
</script>
