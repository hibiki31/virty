<template>
<div>
  <v-dialog width="800" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>Set SSH Key</v-card-title>
        <v-card-text>
          <v-textarea
          class="text-caption"
          outlined
          clearable
          auto-grow
          label="Key"
          v-model="requestData.key"
        ></v-textarea>
        <v-textarea
          class="text-caption"
          outlined
          clearable
          auto-grow
          label="Pub"
          v-model="requestData.pub"
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
        url: '/api/auth/key',
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
    axios.get('/api/auth/key').then(res => {
      this.requestData.key = res.data.private_key;
      this.requestData.pub = res.data.publick_key;
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
