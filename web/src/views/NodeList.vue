<template>
  <div>
    <NodeAddDialog ref="nodeAddDialog" />
    <NodeDeleteDialog ref="nodeDeleteDialog" />
    <v-card>
      <v-card-actions>
        <v-btn v-on:click="this.openNodeAddDialog" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>JOIN
        </v-btn>
        <v-btn v-on:click="this.openNodeDeleteDialog" small dark class="ma-2" color="red">
        <v-icon left>mdi-server-remove</v-icon>LEAVE
      </v-btn>
      </v-card-actions>
      <v-data-table
        :headers="headers"
        :items="list"
        :items-per-page="10"
        :footer-props="{
      'items-per-page-options': [10, 20, 50, 100],
      showFirstLastPage: true,
        }"
        multi-sort
      >
        <template v-slot:[`item.osName`]="{ item }">{{item.osName+' '+item.osVersion}}</template>

        <template v-slot:[`item.status`]="{ item }">
          <v-icon left :color="getStatusColor(item.status)">mdi-check-circle</v-icon>
        </template>

        <template v-slot:[`item.memory`]="{ item }" justify="right">
          <v-icon left>mdi-memory</v-icon>
          {{ item.memory|toFixed}} G
        </template>

      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import NodeAddDialog from '../conponents/dialog/NodeAddDialog';
import NodeDeleteDialog from '../conponents/dialog/NodeDeleteDialog';

export default {
  name: 'NodeList',
  components: {
    NodeAddDialog,
    NodeDeleteDialog
  },
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'Status', value: 'status' },
        { text: 'Name', value: 'name' },
        { text: 'IP', value: 'domain' },
        { text: 'Port', value: 'port' },
        { text: 'Core', value: 'core' },
        { text: 'Memory', value: 'memory' },
        { text: 'CPU', value: 'cpuGen' },
        { text: 'OS', value: 'osName' },
        { text: 'QEMU', value: 'qemuVersion' },
        { text: 'Libvirt', value: 'libvirtVersion' }
      ]
    };
  },
  mounted: async function() {
    axios.get('/api/nodes').then((response) => (this.list = response.data));
  },
  methods: {
    openNodeAddDialog() {
      this.$refs.nodeAddDialog.openDialog();
    },
    openNodeDeleteDialog() {
      this.$refs.nodeDeleteDialog.openDialog(this.list);
    },
    getStatusColor(statusCode) {
      if (statusCode === 10) return 'primary';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'red';
      else return 'yellow';
    }
  },
  filters: {
    toFixed: function(val) {
      if (isFinite(val)) {
        return Number(val).toFixed(0);
      }
      return 0;
    }
  }
};
</script>
