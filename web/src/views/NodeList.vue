<template>
  <div>
    <v-dialog width="400" v-model="nodeDeleteDialog">
      <v-card>
        <v-form ref="nodeDeleteForm">
        <v-card-text>
          <v-select
            :items="list"
            item-text="name"
            item-value="name"
            v-model="nodeName"
            label="Select node name"
            :rules="[required]"
          ></v-select>
        </v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red" dark v-on:click="nodeDelete">LEAVE</v-btn>
        </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
    <v-dialog width="400" v-model="nodeAddDialog">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>Join node</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="nodeName"
              label="Name"
              :rules="[required, limitLength64, characterRestrictions, firstCharacterRestrictions]"
              counter="64"
            ></v-text-field>
            <v-text-field v-model="nodeUser" label="User" :rules="[required]"></v-text-field>
            <v-text-field v-model="nodeIp" label="IP" :rules="[required]"></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="nodeAdd">JOIN</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
    <v-card>
      <v-card-actions>
        <v-btn v-on:click="nodeAddDialog=true" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>JOIN
        </v-btn>
        <v-btn v-on:click="nodeDeleteDialog=true" small dark class="ma-2" color="red">
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
        <template v-slot:item.osName="{ item }">{{item.osName+' '+item.osVersion}}</template>

        <template v-slot:item.status="{ item }">
          <v-icon left :color="getPowerColor(item.status)">mdi-check-circle</v-icon>
        </template>

        <template v-slot:item.memory="{ item }" justify="right">
          <v-icon left>mdi-memory</v-icon>
          {{ item.memory|toFixed}} G
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NodeList',
  data: function() {
    return {
      nodeAddDialog: false,
      nodeDeleteDialog: false,
      nodeName: '',
      nodeUser: '',
      nodeIp: '',
      list: [],
      headers: [
        { text: 'Status', value: 'status' },
        { text: 'Name', value: 'name' },
        { text: 'IP', value: 'ip' },
        { text: 'Core', value: 'core' },
        { text: 'Memory', value: 'memory' },
        { text: 'CPU', value: 'cpugen' },
        { text: 'OS', value: 'osName' },
        { text: 'QEMU', value: 'qemu' },
        { text: 'Libvirt', value: 'libvirt' }
      ]
    };
  },
  mounted: async function() {
    axios.get('/api/nodes').then((response) => (this.list = response.data));
  },
  methods: {
    nodeAdd() {
      if (this.$refs.nodeAddForm.validate()) {
        this.nodeAddDialog = false;
        axios
          .post('/api/queue/node/base', {
            name: this.nodeName,
            user: this.nodeUser,
            ip: this.nodeIp
          })
          .then((res) => {
            if (res.status !== 200) {
              this.$_pushNotice('An error occurred', 'error');
              return;
            }
            this.$_pushNotice('Queueing node add task', 'success');
          })
          .catch(async() => {
            await this.$_sleep(500);
            this.$_pushNotice('An error occurred', 'error');
          });
      }
    },
    nodeDelete() {
      if (this.$refs.nodeDeleteForm.validate()) {
        this.nodeDeleteDialog = false;
        axios
          .delete('/api/queue/node/base', {
            data: {
              name: this.nodeName
            }
          })
          .then((res) => {
            if (res.status !== 200) {
              this.$_pushNotice('An error occurred', 'error');
              return;
            }
            this.$_pushNotice('Queueing node delete task', 'success');
          })
          .catch(async() => {
            await this.$_sleep(500);
            this.$_pushNotice('An error occurred', 'error');
          });
      }
    },
    getPowerColor(statusCode) {
      if (statusCode === 10) return 'primary';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'red';
      else return 'yellow';
    },
    required: (value) => !!value || 'Required.',
    limitLength64: (value) => value.length <= 64 || '64 characters maximum.',
    characterRestrictions(value) {
      const regex = new RegExp(/^[A-Za-z0-9-_]*$/);
      return regex.test(value) || 'Can use character A-Z, a-z, 0-9, -, _';
    },
    firstCharacterRestrictions(value) {
      const regex = new RegExp(/^[A-Za-z].*/);
      return regex.test(value) || 'Can use first character A-Z, a-z';
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
