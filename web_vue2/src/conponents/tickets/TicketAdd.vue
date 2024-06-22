<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="ticketAdd">
          <v-card-title>Add Ticket</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="postData.name"
              label="Name"
              :rules="[$required]"
              counter="64"
            ></v-text-field>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="postData.core"
                  label="Cores"
                  suffix="core"
                  :rules="[$required, $intValueRestrictions]"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="postData.memory"
                  label="Memory"
                  suffix="MB"
                  :rules="[$required, $intValueRestrictions]"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="postData.storageCapacityG"
                  label="Storage"
                  :rules="[$required, $intValueRestrictions]"
                  suffix="GB"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-select
              v-model="postData.flavors"
              :items="itemsFlavors"
              :menu-props="{ maxHeight: '400' }"
              item-text="name"
              item-value="id"
              label="Flavors"
              multiple
              hint="Pick flavor"
              persistent-hint
            ></v-select>
            <v-select
              v-model="postData.storagePools"
              :items="itemsStorages"
              :menu-props="{ maxHeight: '400' }"
              item-text="name"
              item-value="id"
              label="Storage Pools"
              multiple
              persistent-hint
            ></v-select>
            <v-select
              v-model="postData.networkPools"
              :items="itemsNetworks"
              :menu-props="{ maxHeight: '400' }"
              item-text="name"
              item-value="id"
              label="Network Pools"
              multiple
              persistent-hint
            ></v-select>
             <v-checkbox
              v-model="postData.userInstallable"
              label="User installable"
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
      itemsFlavors: [],
      itemsNetworks: [],
      itemsStorages: [],
      postData: {
        name: 'Basic Ticket',
        core: 8,
        memory: 8192,
        storageCapacityG: 32,
        networkPools: [
        ],
        storagePools: [
        ],
        flavors: [
        ],
        userInstallable: true,
        isolatedNetworks: 0
      },
      dialogState: false
    };
  },
  methods: {
    openDialog() {
      this.dialogState = true;
    },
    runMethod() {
      if (!this.$refs.ticketAdd.validate()) {
        return;
      }
      axios.request({
        method: 'post',
        url: '/api/tickets',
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
    axios.get('/api/networks/pools').then((response) => (this.itemsNetworks = response.data));
    axios.get('/api/storages/pools').then((response) => (this.itemsStorages = response.data));
    axios.get('/api/flavors').then((response) => (this.itemsFlavors = response.data));
  }
};
</script>
