<template>
<div>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>User add</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="postData.userId"
            label="Username"
            :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
            counter="64"
          ></v-text-field>
          <v-text-field
            v-model="postData.password"
            :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[$required]"
            :type="show1 ? 'text' : 'password'"
            name="input-10-1"
            label="Password"
            hint="At least 1 characters"
            counter
            @click:append="show1 = !show1"
          ></v-text-field>
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
  name: 'UserAddDialog',
  data: function() {
    return {
      postData: {
        id: '',
        password: ''
      },
      show1: false,
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
        url: '/api/users',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Create successful', 'success');
          this.submitting = false;
          this.$emit('reload');
          this.dialogState = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  }
};
</script>
