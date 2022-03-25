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
              :items="itemsProjects"
              item-text="id"
              item-value="id"
              v-model="postData.projectId"
              label="Select project"
              :rules="[required]"
            >
              <template v-slot:item="{ item }">
                <span>{{ item.id }} - {{ item.name }}</span>
                <v-chip
                  v-for="user in item.users"
                  :key="user.id"
                  x-small
                  class="ma-2"
                >
                  {{ user.id }}
                </v-chip>
              </template>
              <template v-slot:selection="{ item }">
                <span>{{ item.id }} - {{ item.name }}</span>
              </template>
            </v-select>
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
      itemsProjects: [],
      itemsTickets: [],
      postData: {
        projectId: '',
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
    axios.get('/api/projects').then((response) => (this.itemsProjects = response.data));
  }
};
</script>
