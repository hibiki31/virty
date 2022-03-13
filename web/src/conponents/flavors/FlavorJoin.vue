<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="joinForm">
          <v-card-title>Join Flavor</v-card-title>
          <v-card-text>
            <div>{{ item.name }}</div>
            <div>{{ item.storage.name }}</div>
            <div>{{ item.storage.node.name }}</div>
             <v-select
              :items="itemsFlavors"
              item-text="name"
              item-value="id"
              v-model="postData.flavorId"
              label="Select flavor"
            >
            </v-select>
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
  name: 'FlavorJoin',
  data: function() {
    return {
      itemsFlavors: [{
        name: ''
      }],
      postData: {
        storageUuid: 'string',
        path: 'string',
        nodeName: 'string',
        flavorId: 0
      },
      dialogState: false,
      item: {
        name: '',
        storage: {
          name: '',
          node: {
            name: ''
          }
        }
      }
    };
  },
  methods: {
    openDialog(item) {
      this.item = item;
      this.postData.storageUuid = item.storageUuid;
      this.postData.path = item.path;
      // this.postData.nodeName = item.storage.node.name;
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.joinForm.validate()) {
        return;
      }
      axios.request({
        method: 'patch',
        url: '/api/images',
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
    axios.get('/api/flavors').then((response) => (this.itemsFlavors = response.data));
  }
};
</script>
