<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="networkPoolAdd">
          <v-card-title>Add Network Pool
          </v-card-title>
          <v-card-text>
            <v-text-field
              v-model="postData.name"
              label="Name"
              :rules="[$required, $limitLength64]"
              counter="64"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">ADD</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NetworkPoolAddDialog',
  data: function() {
    return {
      itemsStorages: [],
      postData: {
        name: ''
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.networkPoolAdd.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/networks/pools',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Please wait for task to complete', 'success');
          this.dialogState = false;
          this.$emit('reload');
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
