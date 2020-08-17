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
  <template v-slot:item.name="{ item }" justify="right">
      <router-link :to="{
        name: 'VMDetail',
        params: {
          uuid: item.uuid
      }}">{{ item.name}}</router-link>
  </template>
  <template v-slot:item.userId="{ item }" justify="right">
    {{item.userId}}
  </template>
  <template v-slot:item.groupId="{ item }" justify="right">
    <p v-if="item.groupId!==null">{{item.groupId}}</p>
    <p v-else>N/A</p>
  </template>
    <template v-slot:item.status="{ item }">
      <v-icon left :color="getPowerColor(item.status)">mdi-check-circle</v-icon>
      {{item.status}}
    </template>
    <template v-slot:item.runTime="{ item }">
      {{ item.runTime | toFixedTow}} s
    </template>
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
        { text: 'TunTime', value: 'runTime' },
        { text: 'Message', value: 'message' }
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
