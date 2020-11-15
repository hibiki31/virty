<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
          タスク履歴を削除
        </v-card-title>
        <v-card-text>実行中、終了分も含め全て削除します</v-card-text>
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
  data: function() {
    return {
      dialogState: false
    };
  },
  name: 'Home',
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      axios.request({
        method: 'delete',
        url: '/api/tasks'
      })
        .then(res => {
          const len = res.data.length;
          this.$_pushNotice(len + '件の履歴を削除しました', 'success');
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
      this.dialogState = false;
    }
  }
};
</script>
