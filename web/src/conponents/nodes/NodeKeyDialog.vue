<template>
<div>
  <v-dialog width="800" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>Administration Key</v-card-title>
        <v-card-text>
           Using this SSH key, Virty manages nodes.
          <v-textarea
          class="text-caption pt-3"
          outlined
          clearable
          auto-grow
          label="Key"
          v-model="requestData.privateKey"
        ></v-textarea>
        <v-textarea
          class="text-caption"
          outlined
          clearable
          auto-grow
          label="Pub"
          v-model="requestData.publicKey"
        ></v-textarea>
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
        key: '',
        pub: ''
      },
      dialogState: false,
      submitting: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.dialogForm.validate()) {
        return;
      }
      this.submitting = true;
      axios.request({
        method: 'post',
        url: '/api/nodes/key',
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
    axios.get('/api/nodes/key').then(res => {
      this.requestData.privateKey = res.data.privateKey;
      this.requestData.publicKey = res.data.publicKey;
    });
  }
};
</script>

<style>
.v-textarea textarea {
  line-height: 1.1rem !important;
  font-family:monospace, serif;
}
</style>
