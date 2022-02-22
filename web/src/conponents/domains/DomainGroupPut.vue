<template>
<div>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>Change owner</v-card-title>
        <v-card-text>
          <v-select
            :items="groups"
            item-text="id"
            item-value="id"
            v-model="requestData.groupId"
            label="Select userid"
            dense
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn :loading="submitting" color="primary" v-on:click="runMethod" >Submit</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</div>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'GroupAddDialog',
  data: function() {
    return {
      requestData: {
        groupId: '',
        uuid: ''
      },
      users: [],
      groups: [],
      importData: {},
      dialogState: false,
      submitting: false
    };
  },
  methods: {
    openDialog(importData) {
      this.importData = importData;
      this.requestData.uuid = importData.uuid;
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.dialogForm.validate()) {
        return;
      }
      this.submitting = true;
      axios.request({
        method: 'patch',
        url: '/api/vms/group',
        data: this.requestData
      })
        .then(res => {
          this.$_pushNotice('Add successful', 'success');
          this.submitting = false;
          this.$emit('reload');
          this.dialogState = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  },
  mounted: async function() {
    axios.get('/api/users').then((response) => (this.users = response.data));
    axios.get('/api/groups').then((response) => (this.groups = response.data));
  }
};
</script>
