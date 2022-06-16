<template>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form>
        <v-card-title>
        Delete Project
        </v-card-title>
        <v-card-text>
          Do you really want to delete this {{ item.name }}({{ item.id }}) project? All associated VMs, images, networks, etc. will be deleted.
        </v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="error" dark v-on:click="runMethod">DELETE</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'ProjectDeleteDialog',
  data: function() {
    return {
      dialogState: false,
      item: {
        name: '',
        id: ''
      }
    };
  },
  methods: {
    openDialog(item) {
      this.dialogState = true;
      this.item = item;
    },
    runMethod() {
      axios.request({
        method: 'delete',
        url: '/api/projects',
        data: { id: this.item.id }
      })
        .then(res => {
          this.$_pushNotice('Node delete successfull', 'success');
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
