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
  <template v-slot:item.capacity="{ item }" justify="right">
    {{item.capacity}}
    <v-progress-linear
      color="primary"
      height="15"
      :value="(item.capacity-item.available)/item.capacity*100"
    ></v-progress-linear>
  </template>
  </v-data-table>
</v-card>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'StorageList',
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Node', value: 'nodeName' },
        { text: 'UUID', value: 'uuid' },
        { text: 'Capacity', value: 'capacity' },
        { text: 'Available', value: 'available' },
        { text: 'Device', value: 'device' },
        { text: 'type', value: 'type' },
        { text: 'Path', value: 'path' }
      ]
    };
  },
  mounted: async function() {
    axios.get('/api/storage').then((response) => (this.list = response.data));
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
