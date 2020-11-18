<template>
<v-card>
  <v-card-actions>
        <v-btn
          v-on:click="this.storageReloadTask"
          small
          dark
          class="ma-2"
          color="primary"
        >
          <v-icon left>mdi-cached</v-icon>Reload
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
  <template v-slot:item.capacity="{ item }" justify="right">
    {{item.capacity}}  GB
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
    axios.get('/api/storages').then((response) => (this.list = response.data));
  },
  methods: {
    storageReloadTask() {
      axios
        .put('/api/images')
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
