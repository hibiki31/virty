<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>Register node</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="postData.name"
              label="Name"
              :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
              counter="64"
            ></v-text-field>
            <v-text-field v-model="postData.userName" label="User" :rules="[required]"></v-text-field>
            <v-text-field v-model="postData.domain" label="IP or Doain" :rules="[required]"></v-text-field>
            <v-text-field
              v-model="postData.port"
              label="Port"
              :rules="[$required, $intValueRestrictions]"
              counter="64"
            ></v-text-field>
            <v-text-field
              v-model="postData.description"
              label="Descriptions"
              counter="128"
            ></v-text-field>
            <v-checkbox
              v-model="postData.libvirtRole"
              label='Provisioning as kvm host'
            ></v-checkbox>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">Register</v-btn>
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
      postData: {
        name: '',
        userName: '',
        domain: '',
        port: 0,
        description: '',
        libvirtRole: true
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.nodeAddForm.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/tasks/nodes',
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
  }
};
</script>
