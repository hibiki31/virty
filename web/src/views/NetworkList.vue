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
  </v-data-table>
</v-card>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NetworkList',
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Bridge', value: 'bridge' },
        { text: 'Node', value: 'node' },
        { text: 'Type', value: 'type' },
        { text: 'UUID', value: 'uuid' },
        { text: 'DHCP', value: 'dhcp' }
      ]
    };
  },
  mounted: async function() {
    axios.get('/api/network').then((response) => (this.list = response.data));
  },
  methods: {
    getPowerColor(statusCode) {
      if (statusCode === 'success') return 'blue';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'red';
      else return 'yellow';
    }
  }
};
</script>
