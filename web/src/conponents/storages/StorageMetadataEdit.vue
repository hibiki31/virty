<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="stoageMetadataEdit">
          <v-card-title>Change metadata</v-card-title>
          <v-card-text>
            <v-select
              :items="itemsDevice"
              v-model="postData.deviceType"
              label="Select device type"
            >
            </v-select>
            <v-select
              :items="itemsProtocol"
              v-model="postData.protocol"
              label="Select protocol"
            >
            </v-select>
            <v-select
              :items="itemsRool"
              v-model="postData.rool"
              label="Select storage rool"
            >
            </v-select>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">change</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  data: function() {
    return {
      itemsNodes: [],
      itemsDevice: [
        { text: 'NVME SSD', value: 'nvme' },
        { text: 'SATA SSD', value: 'ssd' },
        { text: 'HDD', value: 'hdd' },
        { text: 'Ohter', value: 'other' }
      ],
      itemsProtocol: [
        { text: 'Local', value: 'local' },
        { text: 'NFS', value: 'nfs' },
        { text: 'Ohter', value: 'other' }
      ],
      itemsRool: [
        { text: 'VM Image', value: 'img' },
        { text: 'ISO installer', value: 'iso' },
        { text: 'Template Image', value: 'template' },
        { text: 'Cloud-init', value: 'init-iso' }
      ],
      postData: {
        uuid: null,
        rool: null,
        protocol: null,
        deviceType: null
      },
      dialogState: false
    };
  },
  methods: {
    openDialog(item) {
      this.dialogState = true;
      this.item = item;
      this.postData.uuid = item.uuid;
      if (item.metaData != null) {
        this.postData.rool = item.metaData.rool;
        this.postData.protocol = item.metaData.protocol;
        this.postData.deviceType = item.metaData.deviceType;
      }
    },
    runMethod() {
      axios.request({
        method: 'patch',
        url: '/api/storages',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Changed successfully', 'success');
          this.dialogState = false;
          this.item.metaData.rool = this.postData.rool;
          this.item.metaData.protocol = this.postData.protocol;
          this.item.metaData.deviceType = this.postData.deviceType;
          this.$emit('reload');
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
