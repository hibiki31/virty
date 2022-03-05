<template>
<div>
  <v-dialog width="300" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>Set role</v-card-title>
        <v-card-text>
          Assign roles to nodes. The node is built so that it can execute the assigned role. For example, using Ansible.
          <v-select
            :items="roles"
            v-model="requestData.roleName"
            label="Select role"
            :rules="[required]"
          >
          </v-select>
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
      roles: [
        'libvirt'
      ],
      requestData: {
        nodeName: '',
        roleName: ''
      },
      dialogState: false,
      submitting: false
    };
  },
  methods: {
    openDialog(nodeName) {
      this.dialogState = true;
      this.requestData.nodeName = nodeName;
    },
    runMethod() {
      if (!this.$refs.dialogForm.validate()) {
        return;
      }
      this.submitting = true;
      axios.request({
        method: 'patch',
        url: '/api/nodes/role',
        data: this.requestData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
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
  }
};
</script>
