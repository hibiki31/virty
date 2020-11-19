<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
          VMを削除
        </v-card-title>
        <v-card-text>実行中であっても消されます。ディスクイメージは残ります。</v-card-text>
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
            :loading="this.loading"
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
  name: 'DomainDeleteDialog',
  data: function() {
    return {
      loading: false,
      uuid: '',
      dialogState: false,
      items: []
    };
  },
  methods: {
    openDialog(uuid) {
      this.dialogState = true;
      this.uuid = uuid;
    },
    runMethod() {
      this.loading = true;
      axios.request({
        method: 'delete',
        url: '/api/vms',
        data: { uuid: this.uuid }
      })
        .then(res => {
          this.$_pushNotice('Added a task!', 'success');
          axios
            .get(`/api/tasks/${res.data.uuid}`, { params: { polling: true, timeout: 30000 } })
            .then(res => {
              this.$_pushNotice('Finished a task!', 'success');
              this.dialogState = false;
              this.loading = false;
              this.$router.push({ name: 'VMList' });
            })
            .catch(error => {
              this.$_pushNotice(error.response.data.detail, 'error');
              this.loading = false;
            });
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
          this.loading = false;
        });
    }
  }
};
</script>
