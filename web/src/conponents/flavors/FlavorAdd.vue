<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>Add Flavor</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="postData.name"
              label="Name"
              :rules="[$required]"
              counter="64"
            ></v-text-field>
            <v-text-field
              v-model="postData.os"
              label="OS"
              :rules="[$required]"
              counter="64"
            ></v-text-field>
            <v-text-field
              v-model="postData.manualUrl"
              label="Document URL"
              :rules="[$required]"
              counter="64"
            ></v-text-field>
            <v-text-field
              v-model="postData.icon"
              label="Icon"
              :rules="[$required]"
              counter="64"
            ></v-text-field>
            <v-text-field
              v-model="postData.description"
              label="Descripttion"
              :rules="[$required]"
              counter="64"
            ></v-text-field>
             <v-checkbox
              v-model="postData.cloudInitReady"
              label="Cloud init ready"
            ></v-checkbox>
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
  name: 'NodeAddDialog',
  data: function() {
    return {
      itemsNodes: [],
      postData: {
        name: 'Ubuntu 20.04.4 LTS (Focal Fossa)',
        os: 'Ubuntu 20.04 x64',
        manualUrl: 'https://',
        icon: 'mdi-pentagon',
        cloudInitReady: true,
        description: 'how to use'
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
        url: '/api/flavors',
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
    axios.get('/api/nodes').then((response) => (this.itemsNodes = response.data));
  }
};
</script>
