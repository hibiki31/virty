<template>
  <div>
    <NodeAddDialog ref="nodeAddDialog" />
    <NodeDeleteDialog ref="nodeDeleteDialog" @reload="reload"/>
    <node-key-dialog ref="nodeKeyDialog"/>
    <node-role-patch ref="nodeRolePatch" />
    <v-card>
      <v-card-actions>
        <v-btn v-on:click="$refs.nodeKeyDialog.openDialog()" small class="ma-2" color="primary">
          <v-icon left>mdi-file-key</v-icon>Administration Key
        </v-btn>
        <v-btn v-on:click="this.openNodeAddDialog" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>Register NODE
        </v-btn>
        <v-btn v-on:click="this.openNodeDeleteDialog" small dark class="ma-2" color="error">
          <v-icon left>mdi-server-remove</v-icon>Deletion NODE
        </v-btn>
      </v-card-actions>
      <v-data-table
        :headers="headers"
        :items="list"
        :loading="loading"
        :items-per-page="10"
        :footer-props="{
      'items-per-page-options': [10, 20, 50, 100],
      showFirstLastPage: true,
        }"
        multi-sort
      >
         <template v-slot:[`item.name`]="{ item }" justify="right">
          <router-link
            :to="{ name: 'NodeDetail', params: { name: item.name } }"
            >{{ item.name }}</router-link
          >
        </template>
        <template v-slot:[`item.osName`]="{ item }">{{item.osName+' '+item.osVersion}}</template>

        <template v-slot:[`item.status`]="{ item }">
          <v-icon left :color="getStatusColor(item.status)">mdi-check-circle</v-icon>
        </template>

        <template v-slot:[`item.memory`]="{ item }" justify="right">
          <v-icon left>mdi-memory</v-icon>
          {{ item.memory|toFixed}} G
        </template>
        <template v-slot:[`item.roles`]="{ item }" justify="right">
          <v-tooltip
            bottom
            v-for="role in item.roles"
            :key="role.roleName"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-chip
                v-bind="attrs"
                v-on="on"
                class="ma-2"
                small
                label
              >
                <v-icon small class="pr-2">{{ getIcon(role.roleName) }}</v-icon>
                {{ role.roleName }}
              </v-chip>
            </template>
            <span>{{ role.extraJson }}</span>
          </v-tooltip>
        </template>
        <template v-slot:[`item.actions`]="{ item }" justify="right">
          <v-btn @click="$refs.nodeRolePatch.openDialog(item.name)" icon><v-icon>mdi-flask-empty-plus-outline</v-icon></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import NodeAddDialog from '../conponents/nodes/NodeAddDialog';
import NodeDeleteDialog from '../conponents/nodes/NodeDeleteDialog';
import NodeKeyDialog from '../conponents/nodes/NodeKeyDialog';
import NodeRolePatch from '../conponents/nodes/NodeRolePatch.vue';

export default {
  name: 'NodeList',
  components: {
    NodeAddDialog,
    NodeDeleteDialog,
    NodeKeyDialog,
    NodeRolePatch
  },
  data: function() {
    return {
      list: [],
      loading: false,
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
        { text: 'Libvirt', value: 'libvirtVersion' },
        { text: 'Roles', value: 'roles' },
        { text: 'Actions', value: 'actions' }
      ]
    };
  },
  mounted: async function() {
    this.reload();
  },
  methods: {
    async reload() {
      this.loading = true;
      await axios.get('/api/nodes').then((response) => (this.list = response.data));
      this.loading = false;
    },
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
    },
    getIcon(role) {
      switch (role) {
        case 'ssh': return 'mdi-connection';
        case 'libvirt': return 'mdi-penguin';
        case 'ovs': return 'mdi-lan';
      }
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
