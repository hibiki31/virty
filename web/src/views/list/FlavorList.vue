<template>
<div class="flavor-list">
  <flavor-add ref="flavorAdd" @reload="reload"/>
  <v-card>
    <v-card-actions>
        <v-btn v-on:click="$refs.flavorAdd.openDialog()" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>ADD
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
    </v-data-table>
  </v-card>
</div>
</template>

<script>
import axios from '@/axios/index';
import moment from 'moment';
import FlavorAdd from '@/conponents/flavors/FlavorAdd.vue';

export default {
  name: 'FlavorList',
  components: {
    FlavorAdd
  },
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'name', value: 'name' },
        { text: 'os', value: 'os' },
        { text: 'manualUrl', value: 'manualUrl' },
        { text: 'icon', value: 'icon' },
        { text: 'cloudInitReady', value: 'cloudInitReady' }
      ]
    };
  },
  mounted: function() {
    this.reload();
  },
  methods: {
    reload() {
      axios.get('/api/flavors').then((response) => (this.list = response.data));
    },
    copyClipBoard(text) {
      this.$copyText(text).then(function(e) {
        console.log(e);
      }, function(e) {
        console.log(e);
      });
    },
    openTaskDeleteDialog() {
      this.$refs.taskDeleteDialog.openDialog();
    },
    getStatusColor(statusCode) {
      if (statusCode === 'finish') return 'primary';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'error';
      else return 'yellow';
    },
    getMethodColor(statusCode) {
      if (statusCode === 'add') return 'success';
      else if (statusCode === 'update') return 'primary';
      else if (statusCode === 'delete') return 'error';
      else return 'yellow';
    },
    getResourceIcon(resource) {
      if (resource === 'vm') return 'mdi-cube-outline';
      else if (resource === 'node') return 'mdi-server';
      else if (resource === 'storage') return 'mdi-database';
      else if (resource === 'network') return 'mdi-wan';
      else return 'mdi-help-rhombus';
    }
  },
  filters: {
    toJST: function(date) {
      return moment(date).add(9, 'hour').format('YYYY/MM/DD HH:mm');
    },
    toFixedTow: function(val) {
      if (isFinite(val)) {
        return Number(val).toFixed(2);
      }
      return 0;
    }
  }
};
</script>
