<template>
<div>
  <network-add-dialog ref="networkAddDialog" />
  <network-delete-dialog ref="networkDeleteDialog" />
  <v-card>
    <v-card-actions>
      <v-btn
        v-on:click="networkReloadTask"
        small
        dark
        class="ma-2"
        color="primary"
      >
        <v-icon left>mdi-cached</v-icon>Reload
      </v-btn>
      <!-- 追加ボタン -->
      <v-btn v-on:click="this.openNetworkAddDialog" small class="ma-2" color="primary">
        <v-icon left>mdi-server-plus</v-icon>Add
      </v-btn>
      <!-- 削除ボタン -->
      <v-btn v-on:click="openNetworkDeleteDialog" small dark class="ma-2" color="error">
        <v-icon left>mdi-server-remove</v-icon>Delete
      </v-btn>
    </v-card-actions>
    <v-data-table
      :headers="headers"
      :items="list"
      :items-per-page="10"
      :loading="loading"
      :footer-props="{
        'items-per-page-options': [10, 20, 50, 100],
        showFirstLastPage: true,
          }"
      multi-sort
    >
      <template v-slot:[`item.uuid`]="{ item }" justify="right">
        <router-link
          :to="{ name: 'NetworkDetail', params: { uuid: item.uuid } }"
          style="font-family: monospace;"
          >{{ item.uuid }}</router-link
        >
      </template>
    </v-data-table>
  </v-card>
</div>
</template>

<script>
import axios from '@/axios/index';

import NetworkDeleteDialog from '@/conponents/networks/NetworkDeleteDialog.vue';
import NetworkAddDialog from '@/conponents/networks/NetworkAddDialog.vue';

export default {
  name: 'NetworkList',
  components: {
    NetworkDeleteDialog,
    NetworkAddDialog
  },
  data: function() {
    return {
      list: [],
      loading: false,
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'HostInterface', value: 'hostInterface' },
        { text: 'Node', value: 'nodeName' },
        { text: 'Type', value: 'type' },
        { text: 'UUID', value: 'uuid' },
        { text: 'DHCP', value: 'dhcp' }
      ]
    };
  },
  mounted: async function() {
    this.reload();
  },
  methods: {
    async reload() {
      this.loading = true;
      await axios.get('/api/networks').then((response) => (this.list = response.data));
      this.loading = false;
    },
    openNetworkDeleteDialog() {
      this.$refs.networkDeleteDialog.openDialog(this.list);
    },
    openNetworkAddDialog() {
      this.$refs.networkAddDialog.openDialog();
    },
    networkReloadTask() {
      axios
        .put('/api/networks')
        .then((res) => {
          if (res.status === 401) {
            this.$_pushNotice('Wrong userID or password', 'error');
          } else if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Queueing Relaod task', 'success');
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    },
    getPowerColor(statusCode) {
      if (statusCode === 'success') return 'blue';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'red';
      else return 'yellow';
    }
  }
};
</script>
