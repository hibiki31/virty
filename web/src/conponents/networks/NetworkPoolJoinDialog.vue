<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="joinForm">
          <v-card-title>Join Pool</v-card-title>
          <v-card-text>
            {{ item.name }}
             <v-select
              :items="networkDetail.portgroups"
              item-text="name"
              item-value="name"
              v-model="postData.portName"
              label="Select node name"
            >
            </v-select>
            <v-select
              :items="itemsPools"
              item-text="name"
              item-value="id"
              v-model="postData.poolId"
              label="Select node name"
              :rules="[required]"
            >
            </v-select>
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
  name: 'StoragePoolJoinDialog',
  data: function() {
    return {
      itemsPools: [],
      networkDetail: {},
      postData: {
        id: '',
        storageUuids: []
      },
      dialogState: false,
      item: {}
    };
  },
  methods: {
    openDialog(item) {
      this.item = item;
      this.postData.networkUuid = item.uuid;
      axios.get('/api/networks/' + item.uuid).then((response) => (this.networkDetail = response.data));
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.joinForm.validate()) {
        return;
      }
      axios.request({
        method: 'patch',
        url: '/api/networks/pools',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.$emit('reload');
          this.dialogState = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  },
  mounted: function() {
    axios.get('/api/networks/pools').then((response) => (this.itemsPools = response.data));
  }
};
</script>
