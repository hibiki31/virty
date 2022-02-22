<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>CD Change</v-card-title>
          <v-card-text>
            Pathを空にするとアンマウントします．選択肢はストレージのロールがisoの内容が表示されます．
            <v-text-field v-model="postData.path" label="iso file path" :rules="[]"></v-text-field>
            <v-select v-model="postData.path" :items="isoImages" item-value="path" item-text="name"></v-select>
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
      dialogState: false,
      isoImages: []
    };
  },
  methods: {
    openDialog(target, uuid, node) {
      this.postData.uuid = uuid;
      this.postData.target = target;
      this.dialogState = true;
      axios.get('/api/images', {
        params: {
          rool: 'iso',
          nodeName: node
        }
      }).then((response) => (this.isoImages = response.data));
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
          this.$_pushNotice('Added a task. Please wait for it to complete.', 'success');
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
