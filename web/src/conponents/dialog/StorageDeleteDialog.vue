<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
          ストレージを削除
        </v-card-title>
        <v-card-text>{{this.item.nodeName}}の{{this.item.name}}を削除します。イメージやVMに影響はありません</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="success"
            text
            @click="dialogState = false"
          >
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            text
            @click="runMethod()"
          >
            削除
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
          this.$_pushNotice('Delete success', 'success');
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
      this.dialogState = false;
    }
  }
};
</script>
