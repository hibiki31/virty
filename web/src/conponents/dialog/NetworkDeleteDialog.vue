<template>
<v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="networkDeleteForm">
        <v-card-text>起動中のVMに影響はありません</v-card-text>
        <v-card-text>
          <v-select
            :items="items"
            item-text="name"
            item-value="uuid"
            v-model="uuid"
            label="Select network name"
            :rules="[required]"
          >
            <template v-slot:item="{ item }">
              <span>{{ item.name }}</span>
            </template>
            <template v-slot:selection="{ item }">
              <span>{{ item.name }}</span>
            </template>
          </v-select>
        </v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red" dark v-on:click="runMethod">LEAVE</v-btn>
        </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'networkDeleteDialog',
  data: function() {
    return {
      networkName: '',
      dialogState: false,
      items: [],
      uuid: ''
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
        url: '/api/networks',
        data: { uuid: this.uuid }
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
