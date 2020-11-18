<template>
<v-card>
  <v-card-actions>
        <v-btn
          v-on:click="this.networkReloadTask"
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
    axios.get('/api/networks').then((response) => (this.list = response.data));
  },
  methods: {
    networkReloadTask() {
      axios
        .put('/api/networks')
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
