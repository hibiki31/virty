<template>
  <div>
    <user-add-dialog ref="userAddDialog" @reload="reload"/>
    <v-card>
      <v-card-actions>
        <v-btn
          v-on:click="$refs.userAddDialog.openDialog()"
          small
          dark
          class="ma-2"
          color="primary"
        >
          <v-icon left>mdi-server-plus</v-icon>ADD
        </v-btn>
      </v-card-actions>
      <v-data-table
        :loading="tableLoading"
        :headers="headers"
        :items="user"
        :items-per-page="20"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100, 200, 300, 400, 500],
          showFirstLastPage: true,
        }"
        multi-sort
      >
        <template v-slot:[`item.scopes`]="{ item }" justify="right">
          <v-chip
            v-for="scope in item.scopes"
            :key="scope.name"
            class="ma-2"
            close
            small
          >
            {{ scope.name }}
          </v-chip>
        </template>
        <template v-slot:[`item.groups`]="{ item }" justify="right">
          <v-chip
            v-for="group in item.groups"
            :key="group.id"
            class="ma-2"
            close
            small
          >
            {{ group.id }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import UserAddDialog from '../conponents/users/UserAddDialog.vue';

export default {
  name: 'VMList',
  components: {
    UserAddDialog
  },
  data: function() {
    return {
      tableLoading: true,
      headers: [
        { text: 'id', value: 'id' },
        { text: 'scopes', value: 'scopes' },
        { text: 'groups', value: 'groups' },
        { text: 'actions', value: 'actions' }
      ],
      user: [],
      group: []
    };
  },
  mounted: async function() {
    this.reload();
  },
  methods: {
    async reload() {
      this.tableLoading = true;
      await axios.get('/api/users').then((response) => (this.user = response.data));
      await axios.get('/api/groups').then((response) => (this.group = response.data));
      this.tableLoading = false;
    }
  }
};
</script>
