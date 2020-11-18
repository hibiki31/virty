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
  name: 'ImageList',
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Node', value: 'node' },
        { text: 'Pool', value: 'pool' },
        { text: 'Capacity', value: 'capacity' },
        { text: 'Allocation', value: 'allocation' },
        { text: 'Path', value: 'path' },
        { text: 'Domain Name', value: 'domainName' },
        { text: 'Archive Name', value: 'archiveId' }
      ]
    };
  },
  mounted: async function() {
    axios.get('/api/images').then((response) => (this.list = response.data));
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
