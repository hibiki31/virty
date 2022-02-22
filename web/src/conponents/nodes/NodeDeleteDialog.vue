<template>
<v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeDeleteForm">
        <v-card-text>
          <v-select
            :items="items"
            item-text="name"
            item-value="name"
            v-model="nodeName"
            label="Select node name"
            :rules="[required]"
          >
            <template v-slot:item="{ item }">
              <span>{{ item.name }} - {{ item.domain }}</span>
            </template>
            <template v-slot:selection="{ item }">
              <span>{{ item.name }} - {{ item.domain }}</span>
            </template>
          </v-select>
        </v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="error" dark v-on:click="runMethod">LEAVE</v-btn>
        </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NodeDeleteDialog',
  data: function() {
    return {
      nodeName: '',
      dialogState: false,
      items: []
    };
  },
  methods: {
    openDialog(items) {
      this.dialogState = true;
      this.items = items;
    },
    runMethod() {
      axios.request({
        method: 'delete',
        url: '/api/nodes',
        data: { name: this.nodeName }
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
