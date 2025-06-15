<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>Create Storage Pool
          </v-card-title>
          <v-card-text>
            Add storage of equal speed and fault tolerance to the pool. Abstraction makes it easy to use storage of similar performance on different hosts.<br>
            First, create an empty pool and then register storage for each host that will contain VM images.
            <v-text-field
              v-model="postData.name"
              label="Display name on virty"
              :rules="[$required, $limitLength64]"
              counter="64"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">Create</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NodeAddDialog',
  data: function() {
    return {
      itemsStorages: [],
      postData: {
        name: '',
        storageUuids: []
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.nodeAddForm.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/storages/pools',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.$emit('reload');
          this.dialogState = false;
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  },
  mounted: function() {
  }
};
</script>
