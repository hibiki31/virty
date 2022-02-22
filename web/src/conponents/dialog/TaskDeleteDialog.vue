<template>
<v-dialog
      v-model="dialogState"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
        Delete the task
        </v-card-title>
        <v-card-text>Delete everything, including the running and finished portions. Tasks in progress may be executed incompletely.</v-card-text>
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
          this.$_pushNotice(len + ' tasks history deleted.', 'success');
          this.$emit('reload');
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
      this.dialogState = false;
    }
  }
};
</script>
