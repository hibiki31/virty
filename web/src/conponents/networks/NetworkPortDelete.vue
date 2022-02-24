<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
        Delete the port
        </v-card-title>
        <v-card-text>Delete a oVS port {{ this.postData.name }}. Data will remain and VM will not be affected.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="success"
            text
            @click="dialogState = false"
          >
            chancel
          </v-btn>
          <v-btn
            color="error"
            text
            @click="runMethod()"
          >
            delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'storageDeleteDialog',
  data: function() {
    return {
      dialogState: false,
      item: {},
      postData: {
        uuid: '',
        name: ''
      }
    };
  },
  methods: {
    openDialog(name, uuidNetwork) {
      this.dialogState = true;
      this.postData.uuid = uuidNetwork;
      this.postData.name = name;
    },
    runMethod() {
      axios.request({
        method: 'delete',
        url: '/api/networks/ovs',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
      this.dialogState = false;
    }
  }
};
</script>
