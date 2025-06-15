<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
          Delete the VM
        </v-card-title>
        <v-card-text>Fails if VM is running. The disk image will remain.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="success"
            text
            @click="dialogState = false"
          >
            Cancel
          </v-btn>
          <v-btn
            :loading="this.loading"
            color="error"
            text
            @click="runMethod()"
          >
            Delete
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
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.$router.push({ name: 'VMList' });
          this.dialogState = false;
          this.loading = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
          this.loading = false;
        });
    }
  }
};
</script>
