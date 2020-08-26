<template>
  <v-card>
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
      <template v-slot:item.id="{ item }" justify="right">
        <router-link :to="{name: 'QueueDetail',params: {uuid: item.id}}">{{ item.id}}</router-link>
      </template>
      <template v-slot:item.name="{ item }" justify="right">
        <router-link
          :to="{
        name: 'VMDetail',
        params: {
          uuid: item.uuid
      }}"
        >{{ item.name}}</router-link>
      </template>
      <template v-slot:item.userId="{ item }" justify="right">{{item.userId}}</template>

      <template v-slot:item.method="{ item }" justify="right">
        <v-icon :color="getMethodColor(item.method)">mdi-draw</v-icon>
        {{item.method}}
      </template>

      <template v-slot:item.resource="{ item }" justify="right">
        <v-icon small>{{getResourceIcon(item.resource)}}</v-icon>
        {{item.resource}}
      </template>

      <template v-slot:item.status="{ item }">
        <v-icon left :color="getPowerColor(item.status)">mdi-check-circle</v-icon>
        {{item.status}}
      </template>

      <template v-slot:item.runTime="{ item }">{{ item.runTime | toFixedTow}} s</template>

    </v-data-table>
  </v-card>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'VMList',
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'Status', value: 'status' },
        { text: 'PostTime', value: 'postTime' },
        { text: 'ID', value: 'id' },
        { text: 'Resource', value: 'resource' },
        { text: 'Object', value: 'object' },
        { text: 'Method', value: 'method' },
        { text: 'userId', value: 'userId' },
        { text: 'TunTime', value: 'runTime' }
      ]
    };
  },
  mounted: async function() {
    axios.get('/api/queue').then((response) => (this.list = response.data));
  },
  methods: {
    getPowerColor(statusCode) {
      if (statusCode === 'success') return 'primary';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'red';
      else return 'yellow';
    },
    getMethodColor(statusCode) {
      if (statusCode === 'post') return 'primary';
      else if (statusCode === 'put') return 'blue';
      else if (statusCode === 'delete') return 'red';
      else return 'yellow';
    },
    getResourceIcon(resource) {
      if (resource === 'vm') return 'mdi-home';
      else if (resource === 'node') return 'mdi-server';
      else return 'mdi-gate-not';
    }
  },
  filters: {
    toFixedTow: function(val) {
      if (isFinite(val)) {
        return Number(val).toFixed(2);
      }
      return 0;
    }
  }
};
</script>
