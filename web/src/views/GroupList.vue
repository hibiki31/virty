<template>
  <div>
    <group-add-dialog ref="userAddDialog" @reload="reload"/>
    <group-put-dialog ref="userPutDialog" @reload="reload"/>
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
        :items="group"
        :items-per-page="20"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100, 200, 300, 400, 500],
          showFirstLastPage: true,
        }"
        multi-sort
      >
        <template v-slot:[`item.users`]="{ item }" justify="right">
          <v-chip
            v-for="user in item.users"
            :key="user.id"
            class="ma-2"
            close
            small
          >
            {{ user.id }}
          </v-chip>
        </template>
        <template v-slot:[`item.actions`]="{ item }" justify="right">
          <v-btn
            v-on:click="$refs.userPutDialog.openDialog(item)"
            small
            dark
            class="ma-2"
            color="primary"
            icon
          >
            <v-icon left>mdi-account-multiple-plus</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import GroupAddDialog from '../conponents/groups/GroupAddDialog.vue';
import GroupPutDialog from '../conponents/groups/GroupPutDialog.vue';

export default {
  name: 'VMList',
  components: {
    GroupAddDialog,
    GroupPutDialog
  },
  data: function() {
    return {
      tableLoading: true,
      headers: [
        { text: 'id', value: 'id' },
        { text: 'users', value: 'users' },
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
