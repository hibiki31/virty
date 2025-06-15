<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
        Delete the storage
        </v-card-title>
        <v-card-text>Delete a {{this.item.name}} of {{this.item.nodeName}}. Data will remain and VM will not be affected.</v-card-text>
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
        nodeName: ''
      }
    };
  },
  methods: {
    openDialog(item) {
      this.dialogState = true;
      this.item = item;
      this.postData.uuid = this.item.uuid;
      this.postData.nodeName = this.item.nodeName;
    },
    runMethod() {
      axios.request({
        method: 'delete',
        url: '/api/storages',
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
