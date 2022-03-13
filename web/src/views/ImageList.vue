<template>
<div>
  <flavor-join ref="flavorJoin" />
  <v-card>
    <v-card-title>
      Images
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        @click:append="reload"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="list"
      :items-per-page="10"
      :loading="loading"
      :footer-props="{
        'items-per-page-options': [10, 20, 50, 100],
        showFirstLastPage: true,
          }"
      multi-sort
    >
      <template v-slot:[`item.actions`]="{ item }" justify="right">
        <v-icon v-on:click="$refs.flavorJoin.openDialog(item)" small left>mdi-server-plus</v-icon>
      </template>
      <template v-slot:[`item.path`]="{ item }" justify="right">
        <v-icon @click="copyClipBoard(item.path)" small left>mdi-content-paste</v-icon>
      </template>
    </v-data-table>
  </v-card>
</div>
</template>

<script>
import axios from '@/axios/index';
import FlavorJoin from '../conponents/flavors/FlavorJoin.vue';

export default {
  components: { FlavorJoin },
  name: 'ImageList',
  data: function() {
    return {
      list: [],
      search: '',
      loading: false,
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Node', value: 'storage.node.name' },
        { text: 'Pool', value: 'storage.name' },
        { text: 'Capacity', value: 'capacity' },
        { text: 'Allocation', value: 'allocation' },
        { text: 'Domain Name', value: 'domainName' },
        { text: 'Flavor Name', value: 'flavor.name' },
        { text: 'Path', value: 'path' },
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
      await axios.get('/api/images', {
        params: {
          name: this.search
        }
      }).then((response) => (this.list = response.data));
      this.loading = false;
    },
    copyClipBoard(text) {
      this.$copyText(text).then(function(e) {
        console.log(e);
      }, function(e) {
        console.log(e);
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
