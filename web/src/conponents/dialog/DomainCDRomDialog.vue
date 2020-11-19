<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>CD Change</v-card-title>
          <v-card-text>
            空ならアンマウント
            <v-text-field v-model="postData.path" label="iso file path" :rules="[]"></v-text-field>
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
      postData: {
        path: '',
        target: '',
        uuid: '',
        status: 'mount'
      },
      loadingSubmit: false,
      dialogState: false
    };
  },
  methods: {
    openDialog(target, uuid) {
      this.postData.uuid = uuid;
      this.postData.target = target;
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.nodeAddForm.validate()) {
        return;
      }
      this.loadingSubmit = true;
      axios.request({
        method: 'patch',
        url: '/api/vms',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Added a task!', 'success');
          axios
            .get(`/api/tasks/${res.data.uuid}`, { params: { polling: true, timeout: 30000 } })
            .then(res => {
              this.$_pushNotice('Finished a task!', 'success');
              this.dialogState = false;
              this.loadingSubmit = false;
            })
            .catch(error => {
              this.$_pushNotice(error.response.data.detail, 'error');
              this.loadingSubmit = false;
            });
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  }
};
</script>
