<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="issuanceAdd">
          <v-card-title>Issueance</v-card-title>
          <v-card-text>
            <v-select
              :items="itemsTickets"
              item-text="name"
              item-value="id"
              v-model="postData.ticketId"
              label="Select ticket name"
              :rules="[required]"
            ></v-select>
            <v-select
              :items="itemsUsers"
              item-text="id"
              item-value="id"
              v-model="postData.userId"
              label="Select user name"
              :rules="[required]"
            ></v-select>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">Issueance</v-btn>
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
      itemsUsers: [],
      itemsTickets: [],
      postData: {
        userId: '',
        ticketId: ''
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.issuanceAdd.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/tickets/issuances',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.dialogState = false;
          this.$emit('reload');
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  },
  mounted: function() {
    axios.get('/api/tickets').then((response) => (this.itemsTickets = response.data));
    axios.get('/api/users').then((response) => (this.itemsUsers = response.data));
  }
};
</script>
