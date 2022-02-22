<template>
<div>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form ref="dialogForm">
        <v-card-title>Group add</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="postData.groupId"
            label="Group id"
            :rules="[$required, $limitLength64, $characterRestrictions, $firstCharacterRestrictions]"
            counter="64"
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
  name: 'GroupAddDialog',
  data: function() {
    return {
      postData: {
        groupId: ''
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
        url: '/api/groups',
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
